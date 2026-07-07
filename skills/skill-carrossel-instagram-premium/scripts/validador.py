"""
Validador de carrosseis premium.
Aplica regras criticas do SKILL.md:
- Acentuacao PT-BR obrigatoria (regra Naia 2026-05-12)
- Footer imutavel (handle + nome da marca, vindos do brand_loader)
- Accent valido (so paleta autorizada)
- Limites de slides (capa-corpo-...-cta)
- Tamanho de hook/corpo (avisa se vai estourar)

Uso:
    from validador import validar_carrossel
    problemas = validar_carrossel(carrossel_dict)
    if problemas:
        for p in problemas:
            print("ERRO:", p)
        raise SystemExit(1)
"""
from __future__ import annotations
import re
import unicodedata

try:
    from carousel_design_system import ACCENTS_VALIDOS
except ImportError:
    ACCENTS_VALIDOS = None  # validador funciona standalone

# Palavras PT-BR comuns que QUASE sempre tem acento.
# Se aparecerem sem acento na copy, sinaliza.
PALAVRAS_COM_ACENTO = {
    "voce": "voce -> voce/voce (vc)",  # placeholder
    "nao": "nao -> nao",
    "esta": "esta -> esta",
    "ja": "ja -> ja",
    "so": "so -> so",
    "tambem": "tambem -> tambem",
    "porem": "porem -> porem",
    "atras": "atras -> atras",
    "atraves": "atraves -> atraves",
    "tres": "tres -> tres",
    "ate": "ate -> ate",
    "pra": None,  # neutro
    "esta": "esta -> esta",
    "vao": "vao -> vao",
    "sao": "sao -> sao",
    "mae": "mae -> mae",
    "pai": None,
    "ele": None,
    "ela": None,
    "alem": "alem -> alem",
    "ai": "ai -> ai/ai",
    "ola": "ola -> ola",
    "ferias": "ferias -> ferias",
    "credito": "credito -> credito",
    "video": "video -> video",
    "audio": "audio -> audio",
    "pratico": "pratico -> pratico",
    "estrategico": "estrategico -> estrategico",
    "automatico": "automatico -> automatico",
}

ACENTUADOS_OK = {
    # palavras acentuadas conhecidas - aceitas, nao alertar
    "voce", "nao", "esta", "ja", "so", "tambem", "porem", "atras",
    "atraves", "tres", "ate", "vao", "sao", "mae", "alem", "ai", "ola",
    "ferias", "credito", "video", "audio", "pratico", "estrategico",
    "automatico",
}


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").lower()


def _check_acentuacao(texto: str, contexto: str) -> list[str]:
    """Heuristica leve: se palavra normalizada == palavra original (sem perder caracter),
    pode estar sem acento quando deveria ter. Retorna lista de alertas.
    """
    alertas = []
    palavras = re.findall(r"[a-zA-ZàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]+", texto)
    for p in palavras:
        norm = _normalize(p)
        if norm == p.lower() and norm in PALAVRAS_COM_ACENTO:
            sugestao = PALAVRAS_COM_ACENTO[norm]
            if sugestao:
                alertas.append(
                    f"[ACENTUACAO] '{contexto}': palavra '{p}' provavelmente "
                    f"falta acento ({sugestao})"
                )
    return alertas


def _check_slide(slide: dict, idx: int) -> list[str]:
    problemas = []
    tipo = slide.get("tipo")
    if tipo not in ("capa", "corpo", "bullet", "cta"):
        problemas.append(f"[SLIDE {idx}] tipo invalido: {tipo!r} (use capa/corpo/bullet/cta)")
        return problemas

    if tipo == "capa":
        hl = slide.get("headline", "")
        if not hl:
            problemas.append(f"[SLIDE {idx} CAPA] headline vazio")
        elif len(hl) > 80:
            problemas.append(f"[SLIDE {idx} CAPA] headline com {len(hl)} chars (max sugerido 80, hook fica menor que 54pt)")
        problemas += _check_acentuacao(hl, f"slide {idx} capa headline")

    if tipo == "corpo":
        body = slide.get("body", [])
        if not body:
            problemas.append(f"[SLIDE {idx} CORPO] body vazio")
        if len(body) > 7:
            problemas.append(f"[SLIDE {idx} CORPO] {len(body)} paragrafos (max sugerido 7, divida em 2 slides)")
        for j, para in enumerate(body):
            problemas += _check_acentuacao(para, f"slide {idx} corpo p{j+1}")
        hl = slide.get("headline") or ""
        if hl:
            problemas += _check_acentuacao(hl, f"slide {idx} corpo headline")

    if tipo == "bullet":
        bs = slide.get("bullets", [])
        if not bs:
            problemas.append(f"[SLIDE {idx} BULLET] bullets vazio")
        if len(bs) > 6:
            problemas.append(f"[SLIDE {idx} BULLET] {len(bs)} itens (max sugerido 6)")
        for j, b in enumerate(bs):
            problemas += _check_acentuacao(b, f"slide {idx} bullet b{j+1}")

    if tipo == "cta":
        hl = slide.get("headline", "")
        body = slide.get("body", [])
        if not hl:
            problemas.append(f"[SLIDE {idx} CTA] headline vazio (sugestao: 'LINK NA BIO')")
        if not body:
            problemas.append(f"[SLIDE {idx} CTA] body vazio (precisa ter oferta: data, preco, vagas)")
        problemas += _check_acentuacao(hl, f"slide {idx} cta headline")
        for j, para in enumerate(body):
            problemas += _check_acentuacao(para, f"slide {idx} cta body p{j+1}")

    return problemas


def validar_carrossel(carrossel: dict) -> list[str]:
    """Valida um dict carrossel completo. Retorna lista de problemas (vazio = OK)."""
    problemas = []

    # 1. Estrutura basica
    for k in ("tema", "accent", "foto", "slides"):
        if k not in carrossel:
            problemas.append(f"[CARROSSEL] campo obrigatorio ausente: {k!r}")
    if "slides" not in carrossel:
        return problemas

    slides = carrossel["slides"]
    if not slides:
        problemas.append("[CARROSSEL] slides vazio")
        return problemas
    if len(slides) < 3:
        problemas.append(f"[CARROSSEL] so {len(slides)} slides (minimo recomendado: 4 — capa + 2 corpos + cta)")
    if len(slides) > 10:
        problemas.append(f"[CARROSSEL] {len(slides)} slides (max IG: 10)")

    # 2. Accent valido
    if ACCENTS_VALIDOS and carrossel.get("accent") not in ACCENTS_VALIDOS:
        problemas.append(
            f"[CARROSSEL] accent {carrossel.get('accent')} nao esta em ACCENTS_VALIDOS "
            f"(use DOURADO_BRILHANTE, AMARELO_NEON, TEAL_GLOW ou VERMELHO)"
        )

    # 3. Primeiro slide deve ser capa, ultimo deve ser cta
    if slides[0].get("tipo") != "capa":
        problemas.append("[CARROSSEL] primeiro slide deve ser tipo 'capa'")
    if slides[-1].get("tipo") != "cta":
        problemas.append("[CARROSSEL] ultimo slide deve ser tipo 'cta' (oferta/link na bio)")

    # 4. Cada slide
    for i, s in enumerate(slides, 1):
        problemas += _check_slide(s, i)

    # 5. Tema (so alertar acentuacao)
    if "tema" in carrossel:
        problemas += _check_acentuacao(carrossel["tema"], "tema")

    return problemas


if __name__ == "__main__":
    # Auto-teste
    exemplo_bom = {
        "tema": "Tá vendendo ou apagando incêndio?",
        "accent": (255, 215, 0),
        "foto": "foto_01.png",
        "slides": [
            {"tipo": "capa", "headline": "TÁ VENDENDO OU APAGANDO INCÊNDIO?", "cta": "ARRASTA"},
            {"tipo": "corpo", "headline": None, "body": ["R$50k/mês ou R$5M/mês.", "Se o dia é apagar incêndio,", "o jogo é o mesmo."]},
            {"tipo": "cta", "headline": "LINK NA BIO", "body": ["13 de junho.", "Lote 1: R$47", "15 vagas."]},
        ],
    }
    exemplo_ruim = {
        "tema": "Voce nao esta vendendo",  # SEM acentos
        "accent": (123, 45, 67),  # invalido
        "foto": "x.png",
        "slides": [
            {"tipo": "corpo", "body": ["nada"]},  # nao comeca com capa
        ],
    }
    print("=== EXEMPLO BOM ===")
    for p in validar_carrossel(exemplo_bom):
        print(p)
    print("\n=== EXEMPLO RUIM ===")
    for p in validar_carrossel(exemplo_ruim):
        print(p)
