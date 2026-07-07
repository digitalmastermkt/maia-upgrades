# TYPOGRAPHY_GUIDELINES.md
## Instagram Q&A Cards — Especificação tipográfica oficial

**Autora:** Juliana (Sub-gerente Operacional, Naia Master)
**Data:** 2026-04-30
**Versão:** 1.0
**Persona-alvo:** Dono de padaria de Parnaíba, MEI 35-55a, lendo no celular sob luz forte (sol das 11h da manhã, tela bagunçada de notificação). Precisa LER FÁCIL.

---

## 0. Princípios fundamentais

1. **Legibilidade > estética.** Card bonito que ninguém lê é lixo visual.
2. **O dedão do leitor manda.** Texto principal num único bloco, decisão em 2 segundos: "li ou pulei".
3. **Stories é mais rápido que Feed.** Stories tem 5-7 segundos de atenção. Fonte maior, frase mais curta.
4. **Resposta de Feed pode ser parágrafo.** Mas com palavras-âncora (negrito) pra olho desliza e capta o essencial.
5. **Foto serve ao texto, não o contrário.** Se a foto compete com o texto, a foto perdeu.

---

## 1. Hierarquia tipográfica (canvas 1080px de largura)

### Tabela de elementos

| Elemento | Fonte | Peso | Tamanho px | Line-height | Letter-spacing | Cor |
|---|---|---|---|---|---|---|
| Eyebrow / Categoria | Inter | Medium 500 | 36 | 1.2 | +60 (tracking wide, uppercase) | rgba(255,255,255,0.85) sobre foto / #5B5B7A sobre branco |
| Pergunta (Stories) | Plus Jakarta Sans | ExtraBold 800 | **96** | 1.08 | -10 (tracking tight) | #FFFFFF sobre overlay escuro |
| Pergunta (Feed) | Plus Jakarta Sans | Bold 700 | **72** | 1.12 | -8 | #1A1A2E sobre card claro |
| Resposta corpo | Inter | Regular 400 | **56** | 1.5 | 0 | #1C1C1C sobre card branco |
| Resposta destaque | Inter | Bold 700 | **56** | 1.5 | 0 | #1A1A2E (mesma família, peso muda) |
| Lead da resposta (1ª frase) | Inter | SemiBold 600 | **60** | 1.4 | 0 | #1A1A2E |
| Numeração (01/10) | JetBrains Mono | Medium 500 | 32 | 1.0 | +40 | rgba(255,255,255,0.7) |
| Handle Instagram | Inter | SemiBold 600 | 30 | 1.0 | +20 | rgba(255,255,255,0.85) ou #1A1A2E |
| Marca / Tagline rodapé | Inter | Medium 500 | 26 | 1.0 | +80 (uppercase) | rgba(255,255,255,0.65) |
| CTA "ARRASTE →" | Inter | Bold 700 | 32 | 1.0 | +120 (uppercase) | #FFFFFF |

### Por que essas escolhas

- **Plus Jakarta Sans** no título: aberta, contemporânea, ExtraBold tem peso real sem ficar gritada (diferente da Montserrat Black, que vira parede). Funciona em PT-BR (acentos bem desenhados).
- **Inter** no corpo: desenhada pra UI em telas pequenas. Formas abertas em x-height alto = legibilidade brutal em celular.
- **JetBrains Mono** na numeração: numerais tabulares alinham, dá ar editorial estilo Bloomberg/Forbes (continuidade com carrossel v3 da marca).
- **3 famílias no máximo.** Mais que isso vira bagunça.

### Fallback (caso fonte não carregue)

```
Plus Jakarta Sans → Montserrat → DejaVu Sans Bold → system-ui sans-serif
Inter            → Roboto     → DejaVu Sans       → system-ui sans-serif
JetBrains Mono   → Fira Code  → DejaVu Sans Mono  → monospace
```

---

## 2. Regras de legibilidade (regra de ouro)

### Tamanhos mínimos absolutos (canvas 1080px)
- **Texto principal (pergunta/resposta):** mínimo **48px**. Abaixo disso, descarta o card.
- **Texto secundário (eyebrow, handle):** mínimo **26px**.
- **Texto decorativo (marca rodapé):** mínimo **22px** — e só com letter-spacing aberto.

### Contraste (WCAG AA mínimo, AAA preferido)
- Texto branco sobre foto: **sempre com overlay** (gradient escuro de pelo menos 60% de opacidade na zona do texto). Nunca texto branco direto sobre foto sem overlay.
- Texto escuro sobre card branco: usar **#1A1A2E** ou **#1C1C1C**, nunca cinza médio (#666 ou #888 falham em sol forte).
- Razão de contraste mínima: **4.5:1** (WCAG AA), alvo **7:1** (AAA) para texto principal.
- Proibido: cinza-em-cinza, texto colorido sobre fundo colorido sem overlay, opacidade < 0.85 em texto principal.

### Largura máxima do bloco de texto
- **65% do canvas** para títulos (até 700px de uma largura útil de 1080).
- **88% do canvas** para corpo de resposta (até 950px). Acima disso a linha vira "varredura horizontal" e o leitor desiste.
- Regra ergonômica: **45-65 caracteres por linha** no corpo. Acima de 75 chars/linha = leitura cansa.

### Padding interno (espaço respiratório)
- Card branco de resposta: **48px** de padding em todos os lados (era 22px — DOBRADO).
- Sticker de pergunta: **40px** de padding (era 22px).
- Margem do card até a borda do canvas: **64px** (era 54px).
- Gap entre sticker e card de resposta: **32px** (era 14px).

---

## 3. Variações por tipo de card

### Card de PERGUNTA (Stories 9:16, 1080x1920)

**Hierarquia visual desejada:**
1. Foto domina os primeiros 60% (0-1150px verticais).
2. Eyebrow em 1180px ("PERGUNTA 03 DE 10").
3. Pergunta em 1280px, ocupa **3-4 linhas no máximo**, tipografia esmagadora 96px.
4. Rodapé em 1830px (handle + CTA "ARRASTE →").

**Limite de caracteres:**
- Pergunta: **máximo 80 caracteres**. Se passar, reescrever ou quebrar em 2 cards.
- Eyebrow: **máximo 25 caracteres** (ex: "PERGUNTA 03 DE 10").

**Comportamento se foto tem rosto:**
- Bloco de texto SEMPRE no terço inferior (a partir de 1150px). Nunca sobre o rosto.
- Se mediapipe detectar rosto na metade inferior, descer o texto pra zona segura abaixo do queixo + 12% de margem.

### Card de RESPOSTA (Feed 4:5, 1080x1350)

**Hierarquia visual desejada:**
1. Foto ocupa os primeiros 50% (0-675px). Foto menor que no Stories porque o foco é o texto.
2. Card branco de resposta começa em 720px e cresce conforme o texto exigir.
3. Lead (1ª frase) em SemiBold 60px destacado.
4. Corpo Regular 56px, palavras-âncora em Bold 56px (mesma altura, peso muda — não pula linha).
5. Rodapé pequeno: handle + numeração 06/10 em 1290px.

**Limite de caracteres:**
- Resposta: **máximo 280 caracteres**. Acima disso, dividir em 2 respostas ou cortar.
- Idealmente 4-6 linhas de corpo.

**Tratamento das palavras de destaque:**
- Apenas **1-3 palavras-âncora por resposta**. Mais que isso perde a função.
- Negrito = mesma família tipográfica (Inter Regular vira Inter Bold). Nunca trocar fonte só pra destacar.
- Nunca usar caps, itálico ou cor diferente. Só peso.

---

## 4. Tratamento da foto/fundo

### Estratégias de overlay (escolher baseado na foto)

**A. Overlay gradiente bottom (padrão para Stories)**
- Gradiente vertical, preto opacidade 0 no topo → preto opacidade 0.75 no rodapé.
- Início em 50% da altura do canvas.
- Curva: pow 0.7 (suave, não cinta abrupta).
- Garante que qualquer texto branco no terço inferior seja legível.

**B. Card branco translúcido (padrão para Feed de resposta)**
- Card #FFFFFF opacidade 0.97 (quase opaco) sobre a foto.
- Sombra suave: blur 24px, offset (0, 8), color rgba(0,0,0,0.15).
- Borda arredondada 24px (era 18px — mais editorial).

**C. Bloco escuro sólido (alternativa para perguntas dramáticas)**
- Card #0A0A1A opacidade 0.95.
- Texto branco. Funciona quando a foto tem muita textura/cor que conflita com gradient.

### Posição segura do texto
- **Sempre num quadrante onde a foto NÃO tem detalhes importantes.**
- mediapipe detecta o rosto. Texto SEMPRE abaixo do `face_box.bottom + 0.12` da altura.
- Se rosto está no terço inferior (selfie tipo deitada), inverter: texto no topo com gradient invertido.
- **Nunca sobrepor texto na cara.** Se mediapipe falhou e o texto cair em cima do rosto, regenerar o card.

### Quando a foto tem MÚLTIPLAS pessoas ou cenário muito poluído
- Forçar bloco escuro sólido (estratégia C). Texto sobre foto crua não funciona.
- Alternativa: blur gaussiano leve (raio 4-8px) só na zona do texto, mantendo a foto nítida no resto.

---

## 5. Branding sutil

### Handle Instagram (handle da marca - brand_loader.footer_handle())
- Aparece no rodapé de TODOS os cards.
- Stories: posição 64px da margem esquerda, 1830px do topo (90px do rodapé).
- Feed: posição 64px da margem esquerda, 1290px do topo (60px do rodapé).
- Inter SemiBold 30px, cor branca opacidade 0.85 (Stories) ou #1A1A2E (Feed).
- Sem ícone @-arroba antes — só o texto do handle da marca (brand_loader.footer_handle()).

### Marca / Tagline
- Tagline opcional no rodapé direito: nome da marca (brand_loader.brand_name()) em uppercase, Inter Medium 26px, letter-spacing +80, opacidade 0.65.
- Logo gráfico: NÃO usar nos cards Q&A. Manter simples.

### Numeração da aula
- Stories: canto superior direito, "PERGUNTA 03 / 10" em Inter Medium 28px.
- Feed: rodapé direito, "06 / 10" em JetBrains Mono Medium 32px (numerais monoespaçados ficam alinhados).
- Padrão visual coerente com carrossel v3 (Bloomberg-style).

### CTA Stories: "ARRASTE →"
- Apenas no card 01 (capa) e card 10 (final). Não poluir todos.
- Posição: rodapé direito, espelhado ao handle.
- Inter Bold 32px, uppercase, letter-spacing +120, branco.

---

## 6. Mockups visuais (especificação concreta)

### MOCKUP 1 — STORIES Pergunta (1080x1920)

```
+----------------------------------------------------+ y=0
|                                                    |
|                                                    |
|              [FOTO DA PESSOA ocupa               |
|               60% verticais, smart crop            |
|               com rosto centralizado em            |
|               y=400-800]                           |
|                                                    |
|                                                    |
|                                                    |
+----------------------------------------------------+ y=1150
|  [GRADIENT BOTTOM OVERLAY começa aqui              |
|   alpha 0 → alpha 0.75 até y=1920]                 |
|                                                    |
|  PERGUNTA 03 / 10                                  | y=1180
|  Inter Medium 36px, branco 0.85, tracking +60      |
|                                                    |
|                                                    |
|  COMO USAR IA                                      | y=1280
|  PRA VENDER                                        |
|  MAIS PÃO?                                         |
|  Plus Jakarta Sans ExtraBold 96px                  |
|  branco #FFFFFF, line-height 1.08                  |
|                                                    |
|                                                    |
|                                                    |
|                                                    |
|  @handle              ARRASTE →          | y=1830
|  Inter SemiBold 30px            Inter Bold 32px    |
+----------------------------------------------------+ y=1920

Margem horizontal: 64px de cada lado
Largura útil de texto: 952px
Pergunta com max 3 linhas, ~25 chars/linha
```

### MOCKUP 2 — FEED Resposta (1080x1350)

```
+----------------------------------------------------+ y=0
|                                                    |
|              [FOTO DA PESSOA ocupa               |
|               primeiros 50% (até y=675)            |
|               smart crop centralizado]             |
|                                                    |
|                                                    |
+----------------------------------------------------+ y=675
|  [GRADIENT SUAVE até y=720]                        |
+----------------------------------------------------+ y=720
|  +----------------------------------------------+ |
|  | CARD BRANCO #FFFFFF opacidade 0.97           | |
|  | borda arredondada 24px, sombra blur 24       | |
|  | padding 48px todos os lados                  | |
|  |                                              | |
|  | RESPOSTA 03                                  | | y=780
|  | Inter Medium 32px, #5B5B7A, tracking +60     | |
|  |                                              | |
|  | Comece pelo WhatsApp.                        | | y=840
|  | Inter SemiBold 60px lead, #1A1A2E            | |
|  |                                              | |
|  | Use a IA pra responder cliente em 30         | | y=940
|  | segundos enquanto você assa o pão. Cada      | |
|  | resposta rápida vira venda. Demorou,         | |
|  | perdeu pra concorrência.                     | |
|  | Inter Regular 56px, #1C1C1C, line-height 1.5 | |
|  | Palavras "responder" e "30 segundos" em Bold | |
|  |                                              | |
|  +----------------------------------------------+ |
|                                                    |
|  @handle                       06 / 10   | y=1290
|  Inter SemiBold 30px          JetBrains Mono 32px  |
+----------------------------------------------------+ y=1350

Margem horizontal: 64px
Card de resposta: 952px largura, ~480-600px altura conforme texto
Largura útil de texto dentro do card: 856px (80% canvas)
~32-38 chars/linha em 56px Inter Regular
```

### MOCKUP 3 — STORIES com bloco escuro (foto poluída)

```
+----------------------------------------------------+ y=0
|              [FOTO TEXTURIZADA / múltiplas         |
|               pessoas / cenário poluído]           |
|                                                    |
+----------------------------------------------------+ y=1100
|  +----------------------------------------------+ |
|  | BLOCO ESCURO SÓLIDO #0A0A1A opacidade 0.95   | |
|  | padding 40px                                  | |
|  |                                              | |
|  | PERGUNTA 05 / 10                             | |
|  | Inter Medium 36px, branco 0.85, tracking +60 | |
|  |                                              | |
|  | E SE EU NÃO                                  | | y=1240
|  | TENHO TEMPO                                  | |
|  | PRA APRENDER?                                | |
|  | Plus Jakarta Sans ExtraBold 96px branco      | |
|  |                                              | |
|  +----------------------------------------------+ |
|                                                    |
|  @handle                                 | y=1830
+----------------------------------------------------+ y=1920
```

---

## 7. Acessibilidade (resumo)

- **Tamanho mínimo:** 48px para texto principal, 26px para secundário.
- **Contraste mínimo:** 4.5:1 (WCAG AA). Alvo 7:1 (AAA) para texto principal.
- **Sem itálico em corpo de resposta.** Itálico em sans-serif baixa legibilidade em celular.
- **Sem serif em texto de card.** Serif (Playfair, Merriweather etc.) é elegante mas perde nitidez em px small. Manter sans-serif.
- **Sem texto justificado.** Justificação cria buracos brancos irregulares. Sempre alinhamento à esquerda.
- **Sem ALL CAPS em frase longa.** Caps OK em eyebrow (até 25 chars). Em pergunta de 80 chars, caps cansa o olho.
- **Espaçamento entre cards (no carrossel):** garantir que cada card respira sozinho. Não fazer "continuação" no card seguinte.

---

## 8. Checklist de validação (antes de exportar)

- [ ] Texto principal >= 48px?
- [ ] Razão de contraste >= 4.5:1?
- [ ] Texto está abaixo do `face_box.bottom + 12%`?
- [ ] Pergunta tem <= 80 caracteres?
- [ ] Resposta tem <= 280 caracteres?
- [ ] No máx 3 palavras-âncora em negrito por resposta?
- [ ] Margem horizontal de pelo menos 64px?
- [ ] Padding interno do card >= 48px (resposta) ou 40px (pergunta)?
- [ ] Linha tem 45-65 chars?
- [ ] Há overlay/card sólido entre foto e texto?
- [ ] Handle aparece no rodapé?
- [ ] Numeração presente?

---

## 9. Implementação técnica (notas pra Paulo)

### Fontes — onde baixar e instalar

```
Linux (VPS) — Google Fonts via download direto:
mkdir -p /opt/MAIA/assets/fonts
cd /opt/MAIA/assets/fonts

# Plus Jakarta Sans, Inter, JetBrains Mono
# Baixar zips de fonts.google.com e descompactar em pastas separadas.
```

### Variáveis de ambiente (sugestão)

```
FONT_HEADING="/opt/MAIA/assets/fonts/plus_jakarta/static/PlusJakartaSans-ExtraBold.ttf"
FONT_HEADING_BOLD="/opt/MAIA/assets/fonts/plus_jakarta/static/PlusJakartaSans-Bold.ttf"
FONT_BODY_REG="/opt/MAIA/assets/fonts/inter/static/Inter-Regular.ttf"
FONT_BODY_BOLD="/opt/MAIA/assets/fonts/inter/static/Inter-Bold.ttf"
FONT_BODY_SEMIBOLD="/opt/MAIA/assets/fonts/inter/static/Inter-SemiBold.ttf"
FONT_BODY_MEDIUM="/opt/MAIA/assets/fonts/inter/static/Inter-Medium.ttf"
FONT_MONO="/opt/MAIA/assets/fonts/jetbrains_mono/static/JetBrainsMono-Medium.ttf"
```

### Mudanças necessárias em compose_card.py

1. **Trocar fontes:** Calibri -> Plus Jakarta Sans + Inter + JetBrains Mono.
2. **Aumentar tamanhos:**
   - font_q (pergunta Stories): 40 -> **96**
   - font_q_feed (pergunta Feed): novo, **72**
   - font_ans (resposta corpo): 36 -> **56**
   - font_ans_lead (lead da resposta): novo, **60** SemiBold
   - font_cat (eyebrow): 30 -> **36**
3. **Aumentar padding:** PADDING = 22 -> PADDING_STICKER = 40, PADDING_ANSWER = 48.
4. **Aumentar margem:** MARGIN_RATIO = 0.05 (54px) -> MARGIN_PX = 64.
5. **Aumentar gap:** GAP = 14 -> GAP = 32.
6. **Aumentar corner radius:** CORNER_R = 18 -> CORNER_R = 24.
7. **Adicionar letter-spacing** no eyebrow e marca rodapé (Pillow não tem nativo — implementar `draw_text_with_tracking()` desenhando char por char com offset).
8. **Adicionar lead bold na resposta:** primeira frase (até o primeiro ponto final) em SemiBold 60px, resto Regular 56px.
9. **Validador automático:** após compor, rodar OCR (Tesseract) e medir contraste de cada bloco de texto. Se contraste < 4.5:1 ou texto < 48px, abortar com erro.

### Custo estimado pro Paulo

- **Refactor compose_card.py:** ~90 minutos. Trocar fontes, recalcular layout, criar `draw_text_with_tracking()`, adicionar lead bold.
- **Download e setup das 3 fontes Google na VPS:** ~15 minutos.
- **Testes A/B em 4 cards (2 perguntas + 2 respostas):** ~30 minutos.
- **Total:** ~2h15 de Paulo. Custo IA: zero (Pillow não usa API). Risco: baixo (Pillow estável).

### Validação visual obrigatória

Antes de gerar os 20 cards finais, gerar 1 card de cada formato (Stories pergunta + Feed resposta) e enviar pro responsavel testar:
1. Abrir no celular dele (não no preview do desktop).
2. Sair na rua, sol forte, 11h da manhã.
3. Conseguir ler em 2 segundos sem apertar os olhos.

Se passou no teste do dono de padaria de Parnaíba, está aprovado.
