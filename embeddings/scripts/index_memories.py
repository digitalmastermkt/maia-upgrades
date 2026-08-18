#!/usr/bin/env python3
"""Indexa todas as memórias .md da Maia num banco vetorial (sqlite-vec + Gemini embeddings)."""
import os, sys, sqlite3, pathlib, struct
from dotenv import load_dotenv
import google.generativeai as genai
import sqlite_vec

ENV_PATH = '/opt/MAIA/bot/.env'
MEMORY_DIR = pathlib.Path('/opt/MAIA/memory')
DB_PATH = '/opt/MAIA/embeddings/db/memories.sqlite'
EMBED_MODEL = 'models/gemini-embedding-001'
EMBED_DIM = 3072

def load_env():
    if pathlib.Path(ENV_PATH).exists():
        load_dotenv(ENV_PATH)
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        sys.exit('ERRO: GEMINI_API_KEY não encontrado em .env')
    genai.configure(api_key=key)

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.execute(f'CREATE VIRTUAL TABLE IF NOT EXISTS memories USING vec0(embedding float[{EMBED_DIM}])')
    db.execute('CREATE TABLE IF NOT EXISTS memory_meta (rowid INTEGER PRIMARY KEY, path TEXT UNIQUE, mtime REAL, snippet TEXT)')
    db.commit()
    return db

def embed(text):
    text = text[:8000]
    r = genai.embed_content(model=EMBED_MODEL, content=text, task_type='retrieval_document')
    return r['embedding']

def pack(vec):
    return struct.pack(f'{len(vec)}f', *vec)

def index_file(db, path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    if len(text.strip()) < 20:
        return 'skipped_empty'
    mtime = path.stat().st_mtime
    cur = db.execute('SELECT rowid, mtime FROM memory_meta WHERE path=?', (str(path),)).fetchone()
    if cur and abs(cur[1] - mtime) < 1.0:
        return 'unchanged'
    vec = embed(text)
    snippet = text.replace('\n', ' ')[:200]
    if cur:
        rowid = cur[0]
        db.execute('UPDATE memory_meta SET mtime=?, snippet=? WHERE rowid=?', (mtime, snippet, rowid))
        db.execute('DELETE FROM memories WHERE rowid=?', (rowid,))
        db.execute('INSERT INTO memories(rowid, embedding) VALUES (?, ?)', (rowid, pack(vec)))
        return 'updated'
    else:
        cur2 = db.execute('INSERT INTO memory_meta(path, mtime, snippet) VALUES (?, ?, ?)', (str(path), mtime, snippet))
        rowid = cur2.lastrowid
        db.execute('INSERT INTO memories(rowid, embedding) VALUES (?, ?)', (rowid, pack(vec)))
        return 'inserted'

def main():
    load_env()
    db = init_db()
    counts = {'inserted': 0, 'updated': 0, 'unchanged': 0, 'skipped_empty': 0, 'errors': 0}
    files = sorted(MEMORY_DIR.glob('*.md')) + sorted(MEMORY_DIR.glob('daily/*.md'))
    for f in files:
        try:
            res = index_file(db, f)
            counts[res] = counts.get(res, 0) + 1
            if res in ('inserted', 'updated'):
                print(f'{res}: {f.name}')
        except Exception as e:
            counts['errors'] += 1
            print(f'ERRO em {f.name}: {e}')
    db.commit()
    db.close()
    print(f'\n=== Resumo: {counts} ===')

if __name__ == '__main__':
    main()
