---
name: skill-dossie-sdr
description: Gera dossie completo de pre-abordagem SDR a partir de um @username Instagram. Roda pipeline BMAD (Brand, Market, Audit, Direction) via Gemini 3.1 Pro + Instaloader + scraper de bio. Use quando o usuario pedir "fazer dossie do @username", "analisar perfil X", "preparar abordagem SDR pra X", "BMAD do prospect Y".
triggers:
  - "fazer dossie"
  - "analisar perfil instagram"
  - "BMAD do"
  - "preparar abordagem SDR"
  - "/dossie-sdr"
  - "/bmad"
---

# Skill Dossie SDR — Pipeline BMAD pre-abordagem

Gera dossie completo de analise de prospect Instagram pra SDR usar antes da abordagem.

## Como usar

Quando o usuario pedir analise de um @username Instagram, executar:

```bash
cd /opt/MAIA/workspace/sdr-bmad
python3 run_pipeline.py @username_alvo
```

O pipeline:
1. Coleta dados Instagram via Instaloader (sessao do perfil do negocio configurado em /opt/MAIA/brand/brand.json, via brand_loader)
2. Calcula score local de autenticidade (0-100)
3. Roda 4 chamadas Gemini 3.1 Pro (B, M, A, D - cada um um pilar BMAD)
4. Pesquisa oferta do prospect (link da bio)
5. Monta dossie em /opt/MAIA/workspace/sdr-bmad/output/<username>.md
6. Sobe pro MinIO em seu-bucket/dossies-sdr/

Tempo: ~3 minutos por prospect.
Custo: ~R$1,50 (4 chamadas Gemini Pro).
Limite: 3 prospects/hora (Instaloader rate limit).

## Guia completo

Spec autoritativa esta em /opt/MAIA/knowledge/methods/guia-dossie-treinamento-sdr.md.

Quando criar dossie novo, SEMPRE seguir essa spec. Nao improvisar formato.

## Output

- Dossie .md em /opt/MAIA/workspace/sdr-bmad/output/<username>.md
- Cache JSON em /opt/MAIA/workspace/sdr-bmad/cache/
- Upload MinIO automatico em seu-bucket/dossies-sdr/

## Regras

- Nunca rodar mais de 3 prospects/hora (limite Instagram)
- Sempre validar score BMAD >= 40 antes de classificar como lead viavel
- Dossies de prospects qualificados (score >= 60) viram input do SDR especializado (sdr-instagram, sdr-whatsapp, sdr-linkedin)
