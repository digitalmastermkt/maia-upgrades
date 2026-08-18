---
name: skill-carrossel-instagram-premium
description: "Gera carrosseis premium 1080x1080 pro Instagram da marca, com identidade visual editorial/dark: foto desfocada de fundo + tag monospace teal + headline Plus Jakarta dourada + corpo Inter + footer com handle e nome da marca + CTA flutuante com seta. O handle e o nome do footer vem do sistema central /opt/MAIA/brand/brand.json via brand_loader (footer_handle, brand_name). Inclui 4 templates (capa, corpo, bullet, cta-final dourado), paleta validada, helpers de wrap/centralizacao/blur/gradiente, e validador automatico de acentuacao. Use quando o usuario pedir 'cria carrossel', 'monta carrossel pro feed', 'transforma essa copy em carrossel', 'preciso de cards de carrossel pro Instagram'. Substitui Canva manual em 6h+ por geracao Pillow em ~30s."
---

# Carrossel Instagram Premium

Skill de design system + geracao automatica de carrosseis 1080x1080 com a identidade visual da marca. Handle e nome no footer vem do sistema central `/opt/MAIA/brand/brand.json` via `brand_loader` (`footer_handle`, `brand_name`); nunca hardcode a marca aqui.

## Quando usar

- "Cria um carrossel sobre X"
- "Transforma essa copy em carrossel"
- "Monta carrossel pro lancamento Y"
- "Preciso de 10 carrosseis pro feed"

## Quando NAO usar

- Stories (9:16) - use o template de stories (mesmo design system, dimensoes diferentes)
- Q&A com sticker de pergunta + foto - use `skill-instagram-qa-cards`
- Pagina de vendas - use `skill-pagina-vendas`

## Design system (memorizar)

### Paleta autorizada

| Cor | RGB | Uso |
|---|---|---|
| `DOURADO_BRILHANTE` | (240, 200, 130) | Accent principal (headlines, CTAs, CTA-final fundo) |
| `DOURADO` | (201, 169, 110) | Accent secundario (footer com o nome da marca) |
| `AMARELO_NEON` | (255, 215, 0) | Accent alto-impacto (perguntas, hooks viscerais) |
| `TEAL_GLOW` | (90, 220, 215) | Kicker monospace alternativo, contraste frio |
| `VERMELHO` | (255, 68, 68) | Accent de alarme (testes brutais, dor) |
| `OFFWHITE` | (245, 243, 238) | Corpo de texto sobre fundo escuro |
| `PRETO` | (10, 10, 10) | Box interno, sombras |
| `PRETO_PURO` | (0, 0, 0) | Texto sobre fundo dourado (CTA-final) |
| `CINZA_CLARO` | (180, 180, 180) | Texto secundario, microcopy |

**Regra:** UM accent por carrossel. Define o mood. Nunca misture dourado + amarelo + vermelho no mesmo carrossel.

### Tipografia

| Fonte | Arquivo | Uso |
|---|---|---|
| Plus Jakarta Sans ExtraBold | `assets/fonts/plus_jakarta/PlusJakartaSans-ExtraBold.ttf` | Headlines (54-86pt) |
| Plus Jakarta Sans Bold | `.../PlusJakartaSans-Bold.ttf` | CTAs (20-30pt) |
| Inter Bold | `assets/fonts/inter/Inter-Bold.ttf` | Corpo enfatico (CTA-final) |
| Inter SemiBold | `.../Inter-SemiBold.ttf` | Corpo padrao slides (28-38pt), handle footer (22pt) |
| Inter Medium | `.../Inter-Medium.ttf` | Corpo secundario |
| JetBrains Mono Variable | `assets/fonts/jetbrains_mono/JetBrainsMono-Variable.ttf` | Kickers, indicador, microtags (20-22pt) |

### Layout fixo 1080x1080

- `W=1080, H=1080`
- `PAD=64` (margem lateral)
- `SAFE_TOP=90` (topo, espaco do kicker)
- `SAFE_BOTTOM=130` (rodape: footer + CTA)
- Footer: `H-80` handle da marca (`footer_handle()`), `H-50` nome da marca (`brand_name()`), linha divisora dourada em `H-102`

### Anatomia obrigatoria de TODO slide

```
+----------------------------------+
| // KICKER                01 / 06 |  <- topo
|                                  |
|     [conteudo principal]         |
|                                  |
|                        CTA  ->   |  <- acima do divisor
| -------------------------------- |  <- divisor dourado
| @HANDLE_DA_MARCA                 |  <- footer_handle()
| NOME DA MARCA                    |  <- brand_name()
+----------------------------------+
```

## 4 templates disponiveis

1. **`render_capa`** - Hook gigante centralizado, foto desfocada de fundo, indicador `01/06`, CTA "ARRASTA"
2. **`render_corpo`** - Headline opcional + paragrafos justificados a esquerda, foto desfocada de fundo
3. **`render_bullet`** - Headline + lista de bullets (com prefixo `>` em dourado)
4. **`render_cta_final`** - Fundo dourado solido + box preto centralizado com hook + oferta + "LINK NA BIO"

Todos compoem: `make_background` -> `add_kicker` + `add_slide_indicator` -> conteudo -> `add_footer_and_cta`.

## Fluxo de uso

### Setup (uma vez)

```bash
ls /opt/MAIA/.claude/skills/skill-carrossel-instagram-premium/scripts/
# carousel_design_system.py  <- paleta + fontes + helpers
# templates.py                <- render_capa, render_corpo, render_bullet, render_cta_final
# validador.py                <- checa acentuacao + contraste
# exemplo_uso.py              <- exemplo concreto que voce roda + adapta
```

### Pipeline padrao (3 passos)

**1. Definir CARROSSEIS dict** (estrutura validada):

```python
CARROSSEIS = {
    1: {
        "tema": "Titulo interno descritivo",
        "accent": DOURADO_BRILHANTE,    # ou AMARELO_NEON, VERMELHO, TEAL_GLOW
        "kicker_capa": "// PERGUNTA",   # ou // CASO REAL, // TESTE BRUTAL etc
        "foto": "foto_01.png",          # arquivo em assets/brand/banco_fotos/2026-05/
        "slides": [
            {"tipo": "capa",   "headline": "...", "cta": "ARRASTA"},
            {"tipo": "corpo",  "headline": None, "body": ["linha 1", "linha 2"]},
            {"tipo": "bullet", "headline": "3 SINAIS", "bullets": ["a", "b", "c"]},
            {"tipo": "cta",    "headline": "LINK NA BIO", "body": ["data", "vagas"]},
        ],
    }
}
```

**2. Validar** (acentuacao obrigatoria):

```python
from validador import validar_carrossel
problemas = validar_carrossel(CARROSSEIS[1])
if problemas: raise SystemExit("\n".join(problemas))
```

**3. Renderizar:**

```python
from templates import render_slide
for i, slide in enumerate(carrossel["slides"], 1):
    img = render_slide(carrossel, i, len(carrossel["slides"]))
    img.save(out_dir / f"slide_{i}.png", "PNG", optimize=True)
```

## Foto de fundo - banco a usar

Banco oficial: `/opt/MAIA/assets/brand/banco_fotos/2026-05/` (6 fotos validadas)

Convencao de uso por mood:
- `foto_01.png` (CEO formal navy blazer + cidade) - perguntas duras, autoridade
- `foto_02.png` (casual polo cinza + estudio) - educativo, conversa direta
- `foto_03.png` (apresentando blazer charcoal + cinematico) - capas pesadas, decisao
- `foto_04.png` (escritorio criativo camisa azul) - cases, processo
- `foto_05.png` (estudio editorial gradient escuro) - premium, vinheta de oferta
- `foto_06.png` (coworking moletom navy) - tribo, comunidade

Banco complementar 2026-05-18 (ensaio novo): `assets/brand/banco_fotos/ensaio_2026-05-18/` - 8 cenarios ampliando palco/cafe/celular/institucional.

## Regras criticas

1. **Acentuacao obrigatoria** (regra Maia 2026-05-12): toda copy em PT-BR DEVE ter acentos corretos. Validador derruba o build se faltar.
2. **Footer imutavel**: handle (`footer_handle()`) + nome da marca (`brand_name()`), vindos do `brand_loader`, em TODO slide. Sem excecao.
3. **Indicador `XX / YY` obrigatorio** no canto superior direito de todo slide.
4. **CTA-final** sempre fecha o carrossel.
5. **UM accent por carrossel**. Mudar de accent entre slides = polui marca.
6. **Capa hook em ate 5 linhas** (auto-ajuste de fonte 78->64->54pt). Se passar, reescreva.
7. **Corpo em ate 7 paragrafos** (auto-ajuste 38->28pt). Se passar, vira bullet ou divide em 2 slides.

## Referencias

- Exemplo de uso real validado: `references/exemplo_real_carrosseis_mv.py` (nesta skill)
- Spec de tipografia detalhada: `/opt/MAIA/.claude/skills/skill-instagram-qa-cards/TYPOGRAPHY_GUIDELINES.md` (compartilhado entre Q&A e carrossel)

## Custo e tempo

- 6 slides: ~10s render local (Pillow puro, sem API).
- 10 carrosseis (60 slides): ~90s.
- Custo: R$0 (so CPU). Foto de fundo ja existe no banco - nao chama Gemini.

## Subagentes que usam essa skill

- **jonathan-copy**: escreve a copy estruturada em dict CARROSSEIS
- **paulo-dev**: renderiza/itera/ajusta layouts e adiciona templates novos
- **juliana-ops**: cura design system, valida consistencia, define novos templates
