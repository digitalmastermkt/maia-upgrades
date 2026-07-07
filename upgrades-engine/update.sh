#!/usr/bin/env bash
# ============================================================================
# Digital Master - MAIA Upgrades (pacote PUBLICO)
# update.sh - Orquestrador de upgrade (skills + agentes; memoria opcional)
# ----------------------------------------------------------------------------
# Transforma uma MAIA Aluno (base) numa MAIA Cliente: PLUGA skills + os 7
# agentes no nucleo, SEM tocar na base. Por padrao instala SO skills + agentes
# (copia de pastas/arquivos, seguro pra rodar ao vivo numa aula). A memoria
# semantica (systemd/porta 3007/banco vetorial) so entra com --with-memory.
#
# Fluxo:
#   PASSO 1: detect-version.sh   -> versao atual (de->para no log)
#   PASSO 2: backup-config.sh    -> snapshot antes de mexer
#   PASSO 3: loop install-skill.sh  sobre SKILLS=(...)
#   PASSO 4: loop install-agent.sh  sobre AGENTS=(...)
#   PASSO 5: (opcional --with-memory) instala o servico de memoria semantica
#   PASSO 6: restart do bot      -> systemd ou tmux (se existir)
#   PASSO 7: validate.sh         -> smoke test; se falhar -> rollback.sh
#
# A base (nucleo) NUNCA e reinstalada aqui: este script so PLUGA upgrades.
#
# Uso:
#   sudo bash update.sh                 # skills + agentes (padrao, seguro)
#   sudo bash update.sh --with-memory   # + memoria semantica (avancado)
#
# Todos os caminhos sao RELATIVOS a esta pasta (a copia clonada do repo).
# ============================================================================

set -euo pipefail

# --- Flags ------------------------------------------------------------------
WITH_MEMORY=0
for arg in "$@"; do
  case "$arg" in
    --with-memory) WITH_MEMORY=1 ;;
    -h|--help)
      grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "AVISO: argumento ignorado: $arg" >&2 ;;
  esac
done

# --- Localizacao (tudo relativo a este arquivo) -----------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
INSTALL_DIR="${MAIA_INSTALL_DIR:-$HOME/.maia}"

# Fonte das skills e dos agentes deste pacote (dentro do repo clonado).
SKILLS_SRC="${SKILLS_SRC:-$REPO_ROOT/skills}"
AGENTS_SRC="${AGENTS_SRC:-$REPO_ROOT/agents}"
MEMORY_INSTALLER="$REPO_ROOT/memory-service/install-memory.sh"
NEW_VERSION="${NEW_VERSION:-$( [[ -f "$REPO_ROOT/VERSION" ]] && head -n1 "$REPO_ROOT/VERSION" | tr -d '[:space:]' || echo '' )}"

# --- Manifesto: skills deste pacote (proprias/genericas da Digital Master) ---
SKILLS=(
  "criar-subagente"
  "skill-claude-md-builder"
  "skill-carrossel-instagram-premium"
  "skill-docx"
  "skill-dossie-sdr"
  "skill-instagram-qa-cards"
  "skill-persona-profunda"
  "skill-seguranca-meta-ads"
)

# --- Manifesto: os 7 agentes (o time da MAIA Cliente) -----------------------
AGENTS=(
  "lis"
  "theo"
  "leo"
  "nina"
  "eva"
  "ravi"
  "caio"
)

log() { echo "[$(date +%H:%M:%S)] $*"; }

# =============================== PASSO 1 ====================================
log "PASSO 1/7 - Detectando versao atual"
CURRENT_VERSION="$(bash "$HERE/detect-version.sh" "$INSTALL_DIR" || echo '0.0-desconhecida')"
log "Versao atual: $CURRENT_VERSION"

# =============================== PASSO 2 ====================================
log "PASSO 2/7 - Backup da configuracao"
BACKUP_FILE="$(bash "$HERE/backup-config.sh" "$INSTALL_DIR" | tail -n1)"
log "Backup em: $BACKUP_FILE"

abort_with_rollback() {
  log "ERRO detectado: iniciando rollback."
  bash "$HERE/rollback.sh" "$BACKUP_FILE" "$INSTALL_DIR" || log "AVISO: rollback tambem falhou."
  log "Update abortado e revertido."
  exit 1
}

# =============================== PASSO 3 ====================================
log "PASSO 3/7 - Instalando skills do upgrade (idempotente)"
for skill in "${SKILLS[@]}"; do
  src="$SKILLS_SRC/$skill"
  if [[ ! -d "$src" ]]; then
    log "FALHA: skill nao encontrada na fonte: $src"
    abort_with_rollback
  fi
  if ! bash "$HERE/install-skill.sh" "$src"; then
    log "FALHA ao instalar skill $skill"
    abort_with_rollback
  fi
done

# =============================== PASSO 4 ====================================
log "PASSO 4/7 - Instalando os 7 agentes (idempotente)"
for agent in "${AGENTS[@]}"; do
  src="$AGENTS_SRC/$agent.md"
  if [[ ! -f "$src" ]]; then
    log "FALHA: agente nao encontrado na fonte: $src"
    abort_with_rollback
  fi
  if ! bash "$HERE/install-agent.sh" "$src"; then
    log "FALHA ao instalar agente $agent"
    abort_with_rollback
  fi
done

# =============================== PASSO 5 ====================================
if [[ "$WITH_MEMORY" -eq 1 ]]; then
  log "PASSO 5/7 - Instalando memoria semantica (--with-memory)"
  if [[ ! -x "$MEMORY_INSTALLER" && ! -f "$MEMORY_INSTALLER" ]]; then
    log "FALHA: instalador de memoria nao encontrado: $MEMORY_INSTALLER"
    abort_with_rollback
  fi
  if ! bash "$MEMORY_INSTALLER"; then
    log "FALHA ao instalar a memoria semantica"
    abort_with_rollback
  fi
else
  log "PASSO 5/7 - Memoria semantica PULADA (rode com --with-memory p/ instalar)"
fi

# =============================== PASSO 6 ====================================
log "PASSO 6/7 - Reiniciando o bot (se existir)"
BOT_SERVICE="${MAIA_BOT_SERVICE:-maia-telegram-bot}"
TMUX_SESSION="${MAIA_TMUX_SESSION:-maia}"
if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service 2>/dev/null | grep -q "$BOT_SERVICE"; then
  systemctl restart "$BOT_SERVICE" || { log "FALHA ao reiniciar $BOT_SERVICE"; abort_with_rollback; }
  log "Servico $BOT_SERVICE reiniciado."
elif command -v tmux >/dev/null 2>&1 && tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  tmux send-keys -t "$TMUX_SESSION" C-c
  log "Restart sinalizado na sessao tmux '$TMUX_SESSION'."
else
  log "AVISO: bot nao localizado (systemd/tmux); as skills/agentes ja estao no lugar. Reinicie manualmente se necessario."
fi

# =============================== PASSO 7 ====================================
log "PASSO 7/7 - Validando"
if ! bash "$HERE/validate.sh" "${SKILLS[@]}"; then
  log "Validacao FALHOU."
  abort_with_rollback
fi

# --- Sucesso: grava nova versao (se informada) ------------------------------
if [[ -n "$NEW_VERSION" ]]; then
  mkdir -p "$INSTALL_DIR"
  echo "$NEW_VERSION" > "$INSTALL_DIR/VERSION"
  log "Versao atualizada: $CURRENT_VERSION -> $NEW_VERSION"
fi

log "UPGRADE CONCLUIDO COM SUCESSO. Movimento gera resultado."
exit 0
