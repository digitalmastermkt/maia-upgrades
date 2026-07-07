#!/usr/bin/env bash
# ============================================================================
# Digital Master - MAIA Upgrades
# install-agent.sh - Instalador idempotente de UM agente (.md)
# ----------------------------------------------------------------------------
# Copia UM arquivo de agente para ~/.claude/agents/<nome>.md de forma
# idempotente. Analogo ao install-skill.sh.
# - Resolve o HOME real mesmo rodando sob sudo (via SUDO_USER).
# - Pula a copia se o destino ja estiver identico (cmp -s).
# - Faz chown para o dono correto quando rodado como root.
#
# Uso:
#   ./install-agent.sh <caminho-do-agente.md>
#   sudo ./install-agent.sh /tmp/upg/agents/lis.md
#
# O runtime do Claude Code descobre subagentes lendo ~/.claude/agents/*.md
# (frontmatter YAML: name/description/tools/model). Nao ha registro central.
# ============================================================================

set -euo pipefail

# --- Argumentos -------------------------------------------------------------
AGENT_SRC="${1:-}"

if [[ -z "$AGENT_SRC" ]]; then
  echo "ERRO: informe o caminho do agente. Uso: $0 <caminho-do-agente.md>" >&2
  exit 1
fi

if [[ ! -f "$AGENT_SRC" ]]; then
  echo "ERRO: arquivo de agente nao encontrado: $AGENT_SRC" >&2
  exit 1
fi

# Validacao minima: frontmatter com name.
if ! grep -qE '^name:' "$AGENT_SRC"; then
  echo "ERRO: $AGENT_SRC nao tem frontmatter 'name:' (nao parece um agente valido)." >&2
  exit 1
fi

AGENT_FILE="$(basename "$AGENT_SRC")"

# --- Resolve o HOME real (mesmo sob sudo) -----------------------------------
if [[ -n "${SUDO_USER:-}" && "$SUDO_USER" != "root" ]]; then
  TARGET_USER="$SUDO_USER"
  TARGET_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
else
  TARGET_USER="$(id -un)"
  TARGET_HOME="$HOME"
fi

if [[ -z "$TARGET_HOME" || ! -d "$TARGET_HOME" ]]; then
  echo "ERRO: nao consegui resolver o HOME real do usuario ($TARGET_USER)." >&2
  exit 1
fi

AGENTS_DIR="$TARGET_HOME/.claude/agents"
AGENT_DST="$AGENTS_DIR/$AGENT_FILE"

# --- Idempotencia: pula se ja estiver identico ------------------------------
mkdir -p "$AGENTS_DIR"

if [[ -f "$AGENT_DST" ]] && cmp -s "$AGENT_SRC" "$AGENT_DST"; then
  echo "OK (sem mudancas): agente '$AGENT_FILE' ja esta instalado e identico."
  exit 0
fi

# --- Copia (atualiza ou instala) --------------------------------------------
echo ">> Instalando agente '$AGENT_FILE' em $AGENT_DST"
cp -a "$AGENT_SRC" "$AGENT_DST"

# --- chown para o dono correto (quando root) --------------------------------
if [[ "$(id -u)" -eq 0 && -n "${SUDO_USER:-}" && "$SUDO_USER" != "root" ]]; then
  TARGET_GROUP="$(id -gn "$TARGET_USER" 2>/dev/null || echo "$TARGET_USER")"
  chown "$TARGET_USER:$TARGET_GROUP" "$AGENT_DST"
  echo ">> chown aplicado: $TARGET_USER:$TARGET_GROUP"
fi

echo "OK: agente '$AGENT_FILE' instalado com sucesso."
exit 0
