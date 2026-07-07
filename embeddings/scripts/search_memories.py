#!/usr/bin/env python3
"""Busca semântica nas memórias da Naia. Uso: search_memories.py "consulta" [top_k]"""
import os, sys, sqlite3, pathlib, struct
from dotenv import load_dotenv
import google.generativeai as genai
import sqlite_vec

ENV_PATH = '/opt/MAIA/bot/.env'
DB_PATH = '/opt/MAIA/embeddings/db/memories.sqlite'
EMBED_MODEL = 'models/gemini-embedding-001'

def main():
    if len(sys.argv) < 2:
        sys.exit('Uso: search_memories.py "consulta" [top_k=5]')
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    if pathlib.Path(ENV_PATH).exists():
        load_dotenv(ENV_PATH)
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    r = genai.embed_content(model=EMBED_MODEL, content=query, task_type='retrieval_query')
    qvec = r['embedding']

    db = sqlite3.connect(DB_PATH)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    rows = db.execute(
        '''SELECT m.path, m.snippet, v.distance
           FROM memories v JOIN memory_meta m ON v.rowid = m.rowid
           WHERE v.embedding MATCH ? AND k = ?
           ORDER BY v.distance''',
        (struct.pack(f'{len(qvec)}f', *qvec), top_k)
    ).fetchall()

    print(f'=== Top {len(rows)} resultados para: "{query}" ===\n')
    for i, (path, snippet, dist) in enumerate(rows, 1):
        name = pathlib.Path(path).name
        print(f'{i}. [{dist:.3f}] {name}')
        print(f'   {snippet[:150]}...\n')

if __name__ == '__main__':
    main()
