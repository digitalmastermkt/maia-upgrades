# Changelog — MAIA Upgrades (público)

Convenção de versão: `ANO.MINOR-upgrade-N`.

## 2026.7-upgrade-1

Primeiro pacote público de upgrade da MAIA Cliente.

### Adicionado
- **8 skills** próprias da Digital Master / genéricas em `skills/`:
  `criar-subagente`, `skill-claude-md-builder`,
  `skill-carrossel-instagram-premium`, `skill-docx`, `skill-dossie-sdr`,
  `skill-instagram-qa-cards`, `skill-persona-profunda`,
  `skill-seguranca-meta-ads`.
- **7 agentes** em `agents/`: `lis`, `theo`, `leo`, `nina`, `eva`, `ravi`, `caio`.
- **Motor de upgrade** (`upgrades-engine/`): `update.sh` (skills + agentes,
  com backup/rollback/validação) + novo `install-agent.sh` para plugar os
  agentes em `~/.claude/agents/` resolvendo o HOME real sob sudo.
- **Memória semântica opcional** (`memory-service/` + `embeddings/`): instalada
  só com `--with-memory` — serviço FastAPI na porta 3007, banco SQLite +
  sqlite-vec, unidade systemd `maia-memory.service`.
- `manifest.json`, `README.md`, `.env.TEMPLATE`, `.gitattributes`.

### Observações
- O fluxo **padrão** (sem flag) instala **apenas** skills + agentes — cópia de
  pastas/arquivos, seguro para rodar ao vivo numa aula.
- Nenhuma skill de terceiros foi incluída (repo é público — só IP da casa).
