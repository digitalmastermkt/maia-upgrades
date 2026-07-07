-- ============================================================================
-- Digital Master - MAIA Upgrades / Memoria Semantica (OPCIONAL)
-- schema.sql - Esquema do banco vetorial local (SQLite + sqlite-vec)
-- ----------------------------------------------------------------------------
-- A memoria semantica da MAIA usa SQLite com a extensao sqlite-vec (NAO usa
-- Postgres/pgvector). Embeddings Gemini gemini-embedding-001, 3072 dimensoes.
--
-- Este arquivo e aplicado por install-memory.sh via a extensao sqlite-vec
-- carregada em runtime (a virtual table vec0 exige a extensao carregada; por
-- isso o install-memory.sh executa a criacao por Python, e este .sql serve de
-- documentacao/fonte-unica do esquema).
-- ============================================================================

-- Tabela vetorial: 1 linha por chunk de memoria, embedding float[3072].
CREATE VIRTUAL TABLE IF NOT EXISTS memories USING vec0(embedding float[3072]);

-- Metadados de cada chunk (caminho do .md, mtime, trecho para preview).
CREATE TABLE IF NOT EXISTS memory_meta (
  rowid   INTEGER PRIMARY KEY,
  path    TEXT UNIQUE,
  mtime   REAL,
  snippet TEXT
);
