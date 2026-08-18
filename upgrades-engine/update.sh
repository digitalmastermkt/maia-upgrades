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
#   sudo bash update.sh --premium       # + canal PRIVADO premium (assinante ativo)
#
# --premium (padrao = ENDPOINT): baixa o pacote premium do endpoint HTTP do
# gate (PREMIUM_ENDPOINT), identificando o cliente pelo MESMO slug do phone-home
# (LICENSE_CLIENT_ID em /opt/MAIA/bot/.env). 200 -> tar.gz p/ /tmp, valida
# (tar -tzf), extrai e roda o install-skills.sh dele com o MESMO motor
# (backup->install->validate->rollback), limpando o /tmp. 403 -> "assinatura
# inativa"; 503 -> "pacote indisponivel". FALLBACK: se PREMIUM_TOKEN estiver
# setado (env ou /opt/MAIA/bot/.env), usa o clone git do repo privado. Em
# qualquer falha, o upgrade publico ja aplicado permanece.
#
# Todos os caminhos sao RELATIVOS a esta pasta (a copia clonada do repo).
# ============================================================================

set -euo pipefail

# --- Flags ------------------------------------------------------------------
WITH_MEMORY=0
PREMIUM=0
for arg in "$@"; do
  case "$arg" in
    --with-memory) WITH_MEMORY=1 ;;
    --premium) PREMIUM=1 ;;
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

# --- Canal premium (privado) ------------------------------------------------
# Repo privado com as skills premium. So baixa com token de assinante ativo.
PREMIUM_REPO="${PREMIUM_REPO:-github.com/digitalmastermkt/maia-premium.git}"
# .env da base MAIA de onde tirar PREMIUM_TOKEN (fallback) e o slug do cliente.
BOT_ENV="${MAIA_BOT_ENV:-/opt/MAIA/bot/.env}"
# Endpoint HTTP do gate premium (MODO PADRAO). Valida a licenca do cliente pelo
# slug (LICENSE_CLIENT_ID) e streama o tar.gz do pacote. Vazio = desliga o modo.
PREMIUM_ENDPOINT="${PREMIUM_ENDPOINT:-https://painel.agencianobolso.com.br/premium/package}"
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

# Mensagem unica de acesso negado (nunca vaza token nem URL).
premium_denied() {
  log "ACESSO PREMIUM NEGADO."
  echo "Acesso premium requer assinatura ativa — fale com a Agencia no Bolso." >&2
  return 1
}

# Resolve o slug do cliente EXATAMENTE como o phone-home/verificador: env
# LICENSE_CLIENT_ID, senao a linha LICENSE_CLIENT_ID= do BOT_ENV (/opt/MAIA/bot/.env).
_resolve_slug() {
  local slug="${LICENSE_CLIENT_ID:-}"
  if [[ -z "$slug" && -f "$BOT_ENV" ]]; then
    slug="$(grep -E '^[[:space:]]*LICENSE_CLIENT_ID=' "$BOT_ENV" 2>/dev/null \
             | head -n1 | cut -d= -f2- | tr -d '"'\''[:space:]')"
  fi
  printf '%s' "$slug"
}

# Resolve o PREMIUM_TOKEN (fallback): env, senao a linha do BOT_ENV.
_resolve_premium_token() {
  local token="${PREMIUM_TOKEN:-}"
  if [[ -z "$token" && -f "$BOT_ENV" ]]; then
    token="$(grep -E '^[[:space:]]*PREMIUM_TOKEN=' "$BOT_ENV" 2>/dev/null \
             | head -n1 | cut -d= -f2- | tr -d '"'\''[:space:]')"
  fi
  printf '%s' "$token"
}

# MODO ENDPOINT (padrao): baixa o tar.gz do gate autenticando pelo slug, valida
# o tar ANTES de extrair, e roda o install-skills.sh dele com o MESMO motor.
install_premium_endpoint() {
  local slug; slug="$(_resolve_slug)"
  if [[ -z "$slug" ]]; then
    log "Sem LICENSE_CLIENT_ID (env ou $BOT_ENV) — cliente nao identificavel no endpoint premium."
    premium_denied; return 1
  fi
  if ! command -v curl >/dev/null 2>&1; then
    log "curl ausente — o modo endpoint premium precisa de curl."
    return 1
  fi

  local tmp; tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  local tgz="$tmp/maia-premium.tar.gz" code
  log "Baixando pacote premium do endpoint (assinante ativo)..."
  code="$(curl -sS -o "$tgz" -w '%{http_code}' \
           -H "X-Client-Slug: $slug" \
           "$PREMIUM_ENDPOINT" 2>/dev/null || echo 000)"

  case "$code" in
    200) : ;;
    403) log "Endpoint premium respondeu 403 (assinatura inativa)."
         echo "Assinatura premium inativa — fale com a Agencia no Bolso." >&2
         return 1 ;;
    503) log "Endpoint premium respondeu 503 (pacote indisponivel)."
         echo "Pacote premium indisponivel, tente mais tarde." >&2
         return 1 ;;
    *)   log "Endpoint premium retornou HTTP $code inesperado."
         premium_denied; return 1 ;;
  esac

  # Valida o tar ANTES de extrair (pacote corrompido/HTML de erro nao explode).
  if ! tar -tzf "$tgz" >/dev/null 2>&1; then
    log "Pacote premium invalido (tar -tzf falhou) — abortando overlay."
    return 1
  fi
  mkdir -p "$tmp/pkg"
  if ! tar -xzf "$tgz" -C "$tmp/pkg" >/dev/null 2>&1; then
    log "Falha ao extrair o pacote premium — abortando overlay."
    return 1
  fi
  if [[ ! -f "$tmp/pkg/install-skills.sh" ]]; then
    log "Pacote premium sem install-skills.sh — abortando overlay."
    return 1
  fi

  log "Instalando skills premium (mesmo motor: backup->install->validate)..."
  if ! bash "$tmp/pkg/install-skills.sh"; then
    log "FALHA ao instalar o pacote premium (o install-skills.sh ja reverteu a parte dele)."
    return 1
  fi
  log "Canal premium aplicado com sucesso (via endpoint)."
  return 0
}

# MODO TOKEN (fallback): clone git do repo privado com PREMIUM_TOKEN.
install_premium_token() {
  local token="$1"
  local tmp; tmp="$(mktemp -d)"
  # Limpa o /tmp em qualquer saida da funcao (inclui o token no path do clone).
  trap 'rm -rf "$tmp"' RETURN

  log "Baixando canal premium (privado, via token)..."
  if ! git clone --depth 1 "https://oauth2:${token}@${PREMIUM_REPO}" \
        "$tmp/maia-premium" >/dev/null 2>&1; then
    log "Clone premium falhou (token invalido, assinatura inativa ou 403)."
    premium_denied; return 1
  fi

  if [[ ! -f "$tmp/maia-premium/install-skills.sh" ]]; then
    log "Pacote premium sem install-skills.sh — abortando overlay."
    return 1
  fi

  log "Instalando skills premium (mesmo motor: backup->install->validate)..."
  if ! bash "$tmp/maia-premium/install-skills.sh"; then
    log "FALHA ao instalar o pacote premium (o install-skills.sh ja reverteu a parte dele)."
    return 1
  fi

  log "Canal premium aplicado com sucesso (via token)."
  return 0
}

# Dispatcher: PREMIUM_TOKEN setado (env/BOT_ENV) -> modo token; senao endpoint.
# Nao derruba o upgrade publico ja aplicado: em falha, so retorna != 0.
install_premium() {
  local token; token="$(_resolve_premium_token)"
  if [[ -n "$token" ]]; then
    log "Canal premium: modo TOKEN (PREMIUM_TOKEN presente)."
    install_premium_token "$token"; return $?
  fi
  if [[ -z "$PREMIUM_ENDPOINT" ]]; then
    log "Sem PREMIUM_TOKEN e sem PREMIUM_ENDPOINT — nada a fazer no premium."
    premium_denied; return 1
  fi
  log "Canal premium: modo ENDPOINT (padrao)."
  install_premium_endpoint; return $?
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

# --- Overlay premium (opcional, --premium) ----------------------------------
# Roda DEPOIS do upgrade publico ja validado: se o premium falhar, o publico
# permanece aplicado (nao dispara rollback do publico).
if [[ "$PREMIUM" -eq 1 ]]; then
  log "PREMIUM - Aplicando canal privado (assinante ativo)"
  if install_premium; then
    log "Overlay premium concluido."
  else
    log "Overlay premium NAO aplicado (o upgrade publico continua valido)."
    exit 1
  fi
fi

log "UPGRADE CONCLUIDO COM SUCESSO. Movimento gera resultado."
exit 0
