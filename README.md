# MAIA Upgrades — Pacote público (Digital Master)

> Transforma uma **MAIA Aluno** (base enxuta) numa **MAIA Cliente** completa:
> pluga **8 skills** + os **7 agentes** no núcleo — **sem tocar na base**.
> A memória semântica é **opcional** (só entra com `--with-memory`).
>
> Marca: **Digital Master / Salatiel Batista** — *"Movimento gera resultado."*

---

## O que este pacote instala

**Por padrão (seguro para rodar ao vivo numa aula):**

- **8 skills** em `~/.claude/skills/` (cópia de pastas, autodescobertas pelo Claude Code):
  - `criar-subagente` — cria novos subagentes sob medida
  - `skill-claude-md-builder` — monta o CLAUDE.md do negócio
  - `skill-carrossel-instagram-premium` — carrosséis 1080×1080 premium
  - `skill-docx` — documentos Word com a identidade da marca
  - `skill-dossie-sdr` — dossiê de pré-abordagem SDR (pipeline BMAD)
  - `skill-instagram-qa-cards` — 20 cards de Q&A pro Instagram
  - `skill-persona-profunda` — persona com 30 dimensões + ICP + anti-persona
  - `skill-seguranca-meta-ads` — automação segura da Meta Ads API
- **7 agentes** em `~/.claude/agents/` (o time da MAIA Cliente):
  `lis` (SDR/atendimento), `theo` (copy/pesquisa/persona), `leo` (dev/infra),
  `nina` (coordenação), `eva` (CRM/pós-venda), `ravi` (tráfego), `caio` (projetos).

**Opcional (`--with-memory`, avançado):**

- Serviço de **memória semântica** (busca vetorial HTTP em `127.0.0.1:3007`),
  banco **SQLite + sqlite-vec** (`float[3072]`, embeddings Gemini) e unidade
  **systemd** `maia-memory.service`. Requer uma base MAIA já instalada com
  `GEMINI_API_KEY` no `.env`. **Não** roda no fluxo padrão da aula.

O núcleo (bot + base) **nunca** é reinstalado nem alterado: os scripts só
**adicionam** pastas/arquivos e (no modo memória) uma unidade systemd nova.

---

## Instalação (público, sem token)

Rode na VPS onde a MAIA Aluno já está instalada:

```bash
git clone https://github.com/digitalmastermkt/maia-upgrades.git /tmp/upg && sudo bash /tmp/upg/upgrades-engine/update.sh && rm -rf /tmp/upg
```

### Com memória semântica (opcional, avançado)

```bash
git clone https://github.com/digitalmastermkt/maia-upgrades.git /tmp/upg && sudo bash /tmp/upg/upgrades-engine/update.sh --with-memory && rm -rf /tmp/upg
```

Depois de instalar, o Claude Code **autodescobre** as skills e agentes no
próximo turno — não precisa reiniciar nada (o `update.sh` já sinaliza o
restart do bot, se ele existir).

### Canal premium (privado, só assinante ativo)

Clientes **recorrentes ativos** têm um pacote extra de skills no repositório
**privado** `maia-premium`. Ele só entra com a flag `--premium`, que exige um
`PREMIUM_TOKEN` (via env ou `/opt/MAIA/bot/.env`):

```bash
sudo PREMIUM_TOKEN=xxxx bash /tmp/upg/upgrades-engine/update.sh --premium
```

O `update.sh` clona o `maia-premium` em `/tmp`, instala com o **mesmo motor**
(backup → install → validate → rollback) e limpa o `/tmp`. Sem token / assinatura
inativa (403), o upgrade público continua aplicado e aparece a mensagem:
*"Acesso premium requer assinatura ativa — fale com a Agência no Bolso"*.

---

## Como funciona (mecânica de upgrade modular)

O orquestrador `upgrades-engine/update.sh` roda em passos, com **backup e
rollback automáticos**:

1. detecta a versão atual;
2. faz **backup** da config (`~/.claude/skills`, `.env`, `VERSION`, …);
3. instala as **skills** (idempotente, via `install-skill.sh`);
4. instala os **7 agentes** (idempotente, via `install-agent.sh`);
5. *(opcional)* instala a **memória semântica** (`--with-memory`);
6. reinicia o bot, se existir (systemd ou tmux);
7. **valida**; se algo falhar, faz **rollback** para o backup.

Todos os `.sh` são **idempotentes** (seguros de rodar de novo) e usam caminhos
**relativos** à pasta clonada. Detalhes da convenção em
[`upgrades-engine/CONVENCAO.md`](upgrades-engine/CONVENCAO.md).

### Variáveis de ambiente úteis

| Variável | Padrão | Papel |
|---|---|---|
| `MAIA_INSTALL_DIR` | `$HOME/.maia` | onde ficam backup/VERSION |
| `MAIA_BOT_SERVICE` | `maia-telegram-bot` | serviço systemd do bot |
| `MAIA_TMUX_SESSION` | `maia` | sessão tmux do bot (fallback) |
| `MAIA_HOME` | `/opt/MAIA` | base MAIA (usado só no `--with-memory`) |
| `MAIA_USER` | `maia` | dono dos arquivos (usado só no `--with-memory`) |

---

## Estrutura do repositório

```
maia-upgrades/
├── skills/                 # 8 skills (propriedade Digital Master / genéricas)
├── agents/                 # 7 agentes (.md)
├── upgrades-engine/        # motor de upgrade (update.sh + helpers)
│   ├── update.sh           # orquestrador (skills + agentes; --with-memory)
│   ├── install-skill.sh    # instala 1 skill (idempotente, resolve HOME sob sudo)
│   ├── install-agent.sh    # instala 1 agente (idempotente, resolve HOME sob sudo)
│   ├── backup-config.sh    # snapshot antes de atualizar
│   ├── rollback.sh         # restaura o backup em caso de falha
│   ├── validate.sh         # smoke test pós-install
│   ├── detect-version.sh   # lê a versão instalada
│   └── CONVENCAO.md        # convenção da mecânica modular
├── memory-service/         # memória semântica OPCIONAL (--with-memory)
│   ├── app.py              # serviço FastAPI (busca semântica, porta 3007)
│   ├── requirements.txt
│   ├── schema.sql          # esquema do banco vetorial (SQLite + sqlite-vec)
│   ├── maia-memory.service # unidade systemd (template)
│   └── install-memory.sh   # instalador do serviço de memória
├── embeddings/scripts/     # indexação e busca de memórias
├── manifest.json           # descrição do pacote "maia-cliente"
├── CHANGELOG.md
└── VERSION
```

---

## Segurança

Este repositório é **público** e contém **apenas** propriedade da Digital
Master / Salatiel. Não há tokens, chaves ou `.env` com valores reais — apenas
placeholders (`.env.TEMPLATE`). As skills puxam a identidade da marca do
sistema central da base (`/opt/MAIA/brand/brand.json`), nunca de segredos
embutidos.

*Torne-se uma pessoa extraordinária. Movimento gera resultado.*
