#!/usr/bin/env bash
# ============================================================================
# Digital Master - MAIA Upgrades / Memoria Semantica (OPCIONAL)
# install-memory.sh - Instala o servico de busca semantica (porta 3007)
# ----------------------------------------------------------------------------
# Chamado por update.sh SOMENTE quando rodado com --with-memory. NAO roda no
# fluxo padrao (aula ao vivo). Instala o servico de memoria semantica sobre uma
# instalacao MAIA existente, SEM tocar no nucleo:
#   1. copia memory-service/ + embeddings/scripts/ para dentro de $MAIA_HOME;
#   2. cria a venv e instala as dependencias (fastapi, uvicorn, sqlite-vec, ...);
#   3. inicializa o banco vetorial SQLite (schema.sql: tabela vec0 + memory_meta);
#   4. instala e ativa a unidade systemd maia-memory.service (127.0.0.1:3007).
#
# Pre-requisitos (a base MAIA ja os satisfaz):
#   - $MAIA_HOME existe (padrao /opt/MAIA), com bot/.env contendo GEMINI_API_KEY;
#   - python3 + venv disponiveis; systemd presente; rodar como root (sudo).
#
# Uso:
#   sudo bash install-memory.sh
#   MAIA_HOME=/opt/MAIA MAIA_USER=maia sudo -E bash install-memory.sh
# ============================================================================

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"      # .../memory-service (no repo clonado)
REPO_ROOT="$(cd "$HERE/.." && pwd)"

MAIA_HOME="${MAIA_HOME:-/opt/MAIA}"
MAIA_USER="${MAIA_USER:-maia}"
ENV_FILE="${MAIA_ENV_FILE:-$MAIA_HOME/bot/.env}"
PY="${PY:-python3}"

log() { echo "[memoria] $*"; }

if [[ "$(id -u)" -ne 0 ]]; then
  echo "ERRO: a instalacao da memoria semantica precisa de root (use sudo)." >&2
  exit 1
fi

if [[ ! -d "$MAIA_HOME" ]]; then
  echo "ERRO: MAIA_HOME nao existe: $MAIA_HOME (a base MAIA precisa estar instalada)." >&2
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]] || ! grep -qE '^GEMINI_API_KEY=' "$ENV_FILE"; then
  echo "ERRO: $ENV_FILE sem GEMINI_API_KEY. A memoria usa embeddings Gemini." >&2
  echo "      Preencha GEMINI_API_KEY no .env da base antes de instalar a memoria." >&2
  exit 1
fi

# --- 1) Copia os artefatos para dentro do MAIA_HOME (sem tocar no nucleo) ----
log "1/4 Copiando memory-service/ e embeddings/scripts/ para $MAIA_HOME"
mkdir -p "$MAIA_HOME/memory-service" "$MAIA_HOME/embeddings/scripts" "$MAIA_HOME/embeddings/db" "$MAIA_HOME/memory"
cp -a "$HERE/app.py"            "$MAIA_HOME/memory-service/app.py"
cp -a "$HERE/requirements.txt" "$MAIA_HOME/memory-service/requirements.txt"
cp -a "$REPO_ROOT/embeddings/scripts/index_memories.py"  "$MAIA_HOME/embeddings/scripts/index_memories.py"
cp -a "$REPO_ROOT/embeddings/scripts/search_memories.py" "$MAIA_HOME/embeddings/scripts/search_memories.py"

# --- 2) venv + dependencias -------------------------------------------------
log "2/4 Criando venv e instalando dependencias"
if [[ ! -x "$MAIA_HOME/memory-service/venv/bin/python" ]]; then
  "$PY" -m venv "$MAIA_HOME/memory-service/venv"
fi
"$MAIA_HOME/memory-service/venv/bin/python" -m pip install --upgrade pip wheel setuptools >/dev/null
"$MAIA_HOME/memory-service/venv/bin/pip" install -r "$MAIA_HOME/memory-service/requirements.txt"

# --- 3) Inicializa o banco vetorial (schema.sql via sqlite-vec) -------------
log "3/4 Inicializando o banco vetorial (sqlite-vec, float[3072])"
DB="$MAIA_HOME/embeddings/db/memories.sqlite"
if [[ ! -f "$DB" ]]; then
  "$MAIA_HOME/memory-service/venv/bin/python" - "$DB" <<'PY'
import sys, sqlite3, sqlite_vec
db = sqlite3.connect(sys.argv[1])
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)
db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS memories USING vec0(embedding float[3072])')
db.execute('CREATE TABLE IF NOT EXISTS memory_meta (rowid INTEGER PRIMARY KEY, path TEXT UNIQUE, mtime REAL, snippet TEXT)')
db.commit(); db.close()
print('banco criado:', sys.argv[1])
PY
else
  log "   banco ja existe, pulando criacao"
fi

# --- 4) Unidade systemd -----------------------------------------------------
log "4/4 Instalando unidade systemd maia-memory.service"
GROUP="$(id -gn "$MAIA_USER" 2>/dev/null || echo "$MAIA_USER")"
sed -e "s#^User=.*#User=$MAIA_USER#" \
    -e "s#^Group=.*#Group=$GROUP#" \
    -e "s#^WorkingDirectory=.*#WorkingDirectory=$MAIA_HOME/memory-service#" \
    -e "s#^EnvironmentFile=.*#EnvironmentFile=$ENV_FILE#" \
    -e "s#^ExecStart=.*#ExecStart=$MAIA_HOME/memory-service/venv/bin/uvicorn app:app --host 127.0.0.1 --port 3007#" \
    "$HERE/maia-memory.service" > /etc/systemd/system/maia-memory.service

chown -R "$MAIA_USER:$GROUP" "$MAIA_HOME/memory-service" "$MAIA_HOME/embeddings" "$MAIA_HOME/memory"

systemctl daemon-reload
systemctl enable maia-memory >/dev/null 2>&1 || true
systemctl restart maia-memory

log "OK: memoria semantica instalada e ativa em 127.0.0.1:3007."
exit 0
