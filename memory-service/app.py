#!/usr/bin/env python3
"""naia-memory — busca semantica HTTP na memoria da Naia.

Bind: 127.0.0.1:3007 (somente localhost).
Indices consultados:
  1. MAIN_DB  — /opt/MAIA/embeddings/db/memories.sqlite (alimentado pelo cron
     root index_memories.py, hora em hora; arquivos .md de ~/.claude/projects/.../memory).
     Aberto SOMENTE LEITURA — nunca escrevemos nele.
  2. EXTRA_DB — extra.sqlite local deste servico, cobre /opt/MAIA/memory/ e
     /opt/MAIA/knowledge/ (que o cron NAO indexa). Reindexado em background
     no boot e a cada 6h por este proprio servico.

Mesmo modelo de embedding do indice existente: Gemini gemini-embedding-001, 3072 dim.
"""
import os
import struct
import sqlite3
import pathlib
import threading
import time
import datetime
import logging
from typing import Optional

from dotenv import load_dotenv
import google.generativeai as genai
import sqlite_vec
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ENV_PATH = '/opt/MAIA/bot/.env'
MAIN_DB = '/opt/MAIA/embeddings/db/memories.sqlite'
EXTRA_DB = '/opt/MAIA/memory-service/extra.sqlite'
EXTRA_DIRS = ['/opt/MAIA/memory', '/opt/MAIA/knowledge']
EMBED_MODEL = 'models/gemini-embedding-001'
EMBED_DIM = 3072
CHUNK_SIZE = 6000
REINDEX_INTERVAL_S = 6 * 3600

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('naia-memory')

load_dotenv(ENV_PATH)
_key = os.getenv('GEMINI_API_KEY')
if not _key:
    raise SystemExit('GEMINI_API_KEY nao encontrado em ' + ENV_PATH)
genai.configure(api_key=_key)


def connect(path: str, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    else:
        db = sqlite3.connect(path)
    db.execute('PRAGMA busy_timeout=30000')
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def embed(text: str, task_type: str):
    r = genai.embed_content(model=EMBED_MODEL, content=text[:8000], task_type=task_type)
    return r['embedding']


def pack(vec):
    return struct.pack(f'{len(vec)}f', *vec)


# ---------------------------------------------------------------- extra index

def init_extra_db():
    db = connect(EXTRA_DB)
    db.execute(f'CREATE VIRTUAL TABLE IF NOT EXISTS extra_vec USING vec0(embedding float[{EMBED_DIM}])')
    db.execute('''CREATE TABLE IF NOT EXISTS extra_meta (
        rowid INTEGER PRIMARY KEY,
        path TEXT NOT NULL,
        chunk_index INTEGER NOT NULL DEFAULT 0,
        mtime REAL NOT NULL,
        content TEXT NOT NULL,
        UNIQUE(path, chunk_index))''')
    db.commit()
    db.close()


def chunk_text(text: str):
    text = text.strip()
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE - 500  # overlap de 500 chars
    return chunks


def reindex_extra():
    """Indexa /opt/MAIA/memory e knowledge no extra.sqlite (incremental por mtime)."""
    db = connect(EXTRA_DB)
    stats = {'indexed': 0, 'unchanged': 0, 'removed': 0, 'errors': 0}
    seen = set()
    files = []
    for d in EXTRA_DIRS:
        files.extend(sorted(pathlib.Path(d).rglob('*.md')))
    for f in files:
        try:
            spath = str(f)
            seen.add(spath)
            mtime = f.stat().st_mtime
            row = db.execute('SELECT mtime FROM extra_meta WHERE path=? AND chunk_index=0',
                             (spath,)).fetchone()
            if row and abs(row[0] - mtime) < 1.0:
                stats['unchanged'] += 1
                continue
            text = f.read_text(encoding='utf-8', errors='ignore')
            if len(text.strip()) < 20:
                continue
            # remove chunks antigos do arquivo
            old = db.execute('SELECT rowid FROM extra_meta WHERE path=?', (spath,)).fetchall()
            for (rid,) in old:
                db.execute('DELETE FROM extra_vec WHERE rowid=?', (rid,))
                db.execute('DELETE FROM extra_meta WHERE rowid=?', (rid,))
            for ci, chunk in enumerate(chunk_text(text)):
                vec = embed(chunk, 'retrieval_document')
                cur = db.execute(
                    'INSERT INTO extra_meta(path, chunk_index, mtime, content) VALUES (?,?,?,?)',
                    (spath, ci, mtime, chunk))
                db.execute('INSERT INTO extra_vec(rowid, embedding) VALUES (?,?)',
                           (cur.lastrowid, pack(vec)))
            db.commit()
            stats['indexed'] += 1
            log.info('indexado: %s', f.name)
        except Exception as e:
            stats['errors'] += 1
            log.warning('erro indexando %s: %s', f, e)
    # remove arquivos deletados do disco
    for (rid, path) in db.execute('SELECT rowid, path FROM extra_meta').fetchall():
        if path not in seen:
            db.execute('DELETE FROM extra_vec WHERE rowid=?', (rid,))
            db.execute('DELETE FROM extra_meta WHERE rowid=?', (rid,))
            stats['removed'] += 1
    db.commit()
    db.close()
    log.info('reindex extra: %s', stats)
    return stats


def reindex_loop():
    while True:
        try:
            reindex_extra()
        except Exception as e:
            log.error('reindex_loop: %s', e)
        time.sleep(REINDEX_INTERVAL_S)


# ---------------------------------------------------------------- busca

def _fmt_date(mtime: float) -> str:
    return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')


def _short_source(path: str) -> str:
    for prefix in ('/opt/MAIA/', '/home/maia/.claude/projects/-opt-MAIA/'):
        if path.startswith(prefix):
            return path[len(prefix):]
    return path


def search_main(qblob: bytes, k: int):
    """Busca no indice do cron (somente leitura). Texto vem do arquivo no disco."""
    out = []
    try:
        db = connect(MAIN_DB, readonly=True)
    except Exception as e:
        log.warning('main db indisponivel: %s', e)
        return out
    try:
        rows = db.execute(
            '''SELECT m.path, m.mtime, m.snippet, v.distance
               FROM memories v JOIN memory_meta m ON v.rowid = m.rowid
               WHERE v.embedding MATCH ? AND k = ?
               ORDER BY v.distance''', (qblob, k)).fetchall()
        for path, mtime, snippet, dist in rows:
            text = snippet or ''
            try:
                text = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')[:700]
            except OSError:
                pass
            out.append({'text': text, 'source': _short_source(path),
                        'date': _fmt_date(mtime), 'distance': dist})
    finally:
        db.close()
    return out


def search_extra(qblob: bytes, k: int):
    out = []
    try:
        db = connect(EXTRA_DB, readonly=True)
    except Exception as e:
        log.warning('extra db indisponivel: %s', e)
        return out
    try:
        rows = db.execute(
            '''SELECT m.path, m.mtime, m.content, v.distance
               FROM extra_vec v JOIN extra_meta m ON v.rowid = m.rowid
               WHERE v.embedding MATCH ? AND k = ?
               ORDER BY v.distance''', (qblob, k)).fetchall()
        for path, mtime, content, dist in rows:
            out.append({'text': content[:700], 'source': _short_source(path),
                        'date': _fmt_date(mtime), 'distance': dist})
    finally:
        db.close()
    return out


# ---------------------------------------------------------------- API

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source: Optional[str] = None


app = FastAPI(title='naia-memory', docs_url=None, redoc_url=None)


@app.on_event('startup')
def _startup():
    init_extra_db()
    threading.Thread(target=reindex_loop, daemon=True).start()


@app.post('/search')
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(400, 'query vazia')
    top_k = max(1, min(req.top_k, 50))
    try:
        qvec = embed(req.query, 'retrieval_query')
    except Exception as e:
        raise HTTPException(502, f'erro gerando embedding da query: {e}')
    qblob = pack(qvec)
    fetch_k = top_k * 4 if req.source else top_k
    results = search_main(qblob, fetch_k) + search_extra(qblob, fetch_k)
    if req.source:
        s = req.source.lower()
        results = [r for r in results if s in r['source'].lower()]
    results.sort(key=lambda r: r['distance'])
    final = []
    for r in results[:top_k]:
        final.append({'text': r['text'], 'source': r['source'], 'date': r['date'],
                      'score': round(1.0 / (1.0 + r['distance']), 4)})
    return {'query': req.query, 'results': final}


@app.get('/health')
def health():
    counts = {}
    try:
        db = connect(MAIN_DB, readonly=True)
        counts['main_index'] = db.execute('SELECT count(*) FROM memory_meta').fetchone()[0]
        db.close()
    except Exception as e:
        counts['main_index'] = f'erro: {e}'
    try:
        db = connect(EXTRA_DB, readonly=True)
        counts['extra_index'] = db.execute('SELECT count(*) FROM extra_meta').fetchone()[0]
        db.close()
    except Exception as e:
        counts['extra_index'] = f'erro: {e}'
    total = sum(v for v in counts.values() if isinstance(v, int))
    return {'status': 'ok', 'indexed_items': total, 'detail': counts,
            'model': EMBED_MODEL, 'dim': EMBED_DIM}
