# Especificacoes de Layout — Instagram Q&A Cards

## Formatos de Canvas

| Formato | Dimensoes | Uso |
|---------|-----------|-----|
| Stories | 1080 x 1920 px (9:16) | Stories e Reels |
| Feed    | 1080 x 1350 px (4:5)  | Feed do Instagram |

## Regras de Posicionamento do Texto

### Zona segura (texto nunca aparece acima destes limites):
- **Stories**: texto comeca a partir de 52% da altura (y >= 998px)
- **Feed**: texto comeca a partir de 60% da altura (y >= 810px)

### Margem de seguranca abaixo do rosto:
- Sempre adicionar 12% da altura do canvas abaixo do `face_box.bottom`
- Ex: rosto termina em 40% → texto comeca em 52% (ou na zona segura, o que for maior)

### Margens horizontais:
- 5% de cada lado (54px em canvas de 1080px)
- Largura de conteudo: 972px

## Design dos Elementos

### Sticker de Pergunta (estilo Instagram nativo)

```
Fundo:           rgba(26, 26, 78, 235)   # indigo escuro, levemente transparente
Borda arredondada: 18px
Padding interno:   22px

Texto categoria (linha superior):
  - Fonte: Calibri Regular, 30px
  - Cor: (165, 165, 210)               # roxo muted
  - Maximo 25 caracteres

Texto pergunta (linha principal):
  - Fonte: Calibri Bold, 40px
  - Cor: (255, 255, 255)               # branco
  - Maximo 80 caracteres
  - Quebra de linha automatica se necessario
  - Line height: 1.5x (60px entre linhas)
```

### Card de Resposta

```
Fundo:           rgba(255, 255, 255, 250) # branco, quase opaco
Borda arredondada: 18px
Padding interno:   22px
Gap acima (do sticker): 14px

Texto resposta:
  - Fonte: Calibri Regular, 36px (palavras em destaque: Bold)
  - Cor: (28, 28, 28)                   # quase preto
  - Maximo 200 caracteres
  - Line height: 1.55x
  - Palavras em 'destaques' ficam em Bold automaticamente
```

### Gradiente de Fundo

Para garantir legibilidade dos cards sobre a foto:
- Gradiente preto começa em 30% da altura
- Opacidade maxima no rodape: 180/255 (alfa)
- Curva: potencia 0.7 (suave, nao abrupto)

## Fallback para Rosto Nao Detectado

Se mediapipe nao detectar o rosto, usa posicao padrao:
```json
{"top": 0.05, "left": 0.15, "bottom": 0.48, "right": 0.85}
```

## Fontes no Windows

Padroes usados pelos scripts (configuravel via variaveis de ambiente):
- `FONT_REGULAR`: `C:\Windows\Fonts\calibri.ttf`
- `FONT_BOLD`: `C:\Windows\Fonts\calibrib.ttf`

Fallback automatico para Arial se Calibri nao disponivel.
Para customizar: defina as variaveis antes de rodar o script.
