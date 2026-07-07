---
name: skill-instagram-qa-cards
description: "Gera automaticamente 20 cards de Instagram (10 perguntas e respostas x 2 formatos - Stories 9:16 + Feed 4:5) a partir de uma transcricao de aula ou live. Cada card tem foto de fundo gerada com IA preservando o rosto da pessoa, sticker de pergunta estilo Instagram e card de resposta com palavras destacadas em negrito. Use quando o usuario quiser criar cards de Q&A para Instagram, gerar conteudo de perguntas e respostas para stories ou feed, automatizar criacao de posts com foto + sticker + resposta, ou transformar transcricao de aula/live em cards prontos."
---

# Instagram Q&A Cards — Pipeline Completo

Gera 20 PNGs prontos para postar (10 Q&A x Stories + Feed) a partir de uma transcricao.
Tempo total: ~5 minutos vs 3-4 horas no Canva manual.

## Inputs necessarios

Antes de comecar, colete:
1. **Transcricao**: arquivo .txt da aula, live ou conteudo (pode ser copia da transcricao do YouTube/WhatsApp)
2. **Fotos de referencia**: 1-3 fotos da pessoa (para gerar fotos com IA) OU 1 foto fixa para usar como fundo
3. **API Key do Google AI Studio**: chave da conta do usuario

## Setup inicial (apenas na primeira vez)

```bash
cd /opt/MAIA/.claude/skills/skill-instagram-qa-cards/scripts

# Instalar dependencias
pip install -r requirements.txt
```

Se mediapipe der erro na instalacao: o pipeline continua funcionando sem ele (usa posicao padrao para o rosto).

## Rodar o pipeline

### Opcao A: Com geracao de fotos por IA (recomendado)
```bash
python run_pipeline.py "C:\caminho\transcricao.txt" --references foto1.jpg foto2.jpg foto3.jpg --api-key SUA_CHAVE_AQUI
```

### Opcao B: Com foto fixa (sem gerar fotos com IA — mais rapido)
```bash
python run_pipeline.py "C:\caminho\transcricao.txt" --photo "C:\caminho\minha_foto.jpg" --api-key SUA_CHAVE_AQUI
```

### Parametros opcionais:
- `--output nome_da_pasta` — pasta de saida (default: `output_cards`)

## O que o pipeline faz (7 etapas automaticas)

1. **Extrai Q&A** — Gemini Flash le a transcricao e gera 10 pares (3 dicas + 2 mentalidade + 2 historias + 2 insights + 1 controverso)
2. **Gera fotos** — Gemini gera uma foto da pessoa por card, preservando rosto/identidade
3. **Detecta rosto** — mediapipe localiza o rosto em cada foto para evitar sobreposicao
4. **Compoe sticker** — sticker de pergunta estilo Instagram (fundo indigo escuro, texto branco)
5. **Compoe resposta** — card branco com palavras-chave em negrito automatico
6. **Monta camadas** — foto + gradiente + sticker + card de resposta
7. **Repete** — 10 cards x 2 formatos = 20 PNGs prontos

## Output

```
output_cards/
  card_01_stories.png    <- Stories 1080x1920 (9:16)
  card_01_feed.png       <- Feed 1080x1350 (4:5)
  card_02_stories.png
  card_02_feed.png
  ... (ate card_10)
  qa_cards.json          <- Q&A gerado (para revisar ou reutilizar)
  _fotos_geradas/        <- Fotos geradas pela IA (se usou --references)
```

## Erros comuns e solucoes

**Erro de modelo de geracao de imagens:**
O nome do modelo Gemini para imagens pode variar. Se `gemini-2.0-flash-preview-image-generation` der erro, abra `generate_photo.py` e troque o modelo por `gemini-2.0-flash-exp-image-generation`. Verifique os modelos disponiveis em aistudio.google.com.

**Fotos geradas nao preservam bem o rosto:**
Forneca 3 fotos de referencia de angulos diferentes (frente, 3/4, perfil). O Gemini faz melhor trabalho com mais referencias.

**Texto cortando no card:**
Perguntas devem ter max 80 chars e respostas max 200 chars. Edite manualmente o arquivo `qa_cards.json` e rode so a composicao novamente com `compose_card.py`.

**mediapipe nao instalado:**
O pipeline continua sem ele usando posicao padrao (rosto na metade superior). Instale com `pip install mediapipe` para posicionamento preciso.

## Customizacao

Para ajustar cores, fontes ou margens: consulte `references/layout_specs.md`
Para ajustar prompts de Q&A ou geracao de foto: consulte `references/prompt_templates.md`
