"""
Exemplo concreto de uso da skill-carrossel-instagram-premium.

Roda standalone:
    cd /opt/MAIA/.claude/skills/skill-carrossel-instagram-premium/scripts
    python3 exemplo_uso.py

Gera 1 carrossel de 4 slides em ./out_exemplo/slide_*.png usando foto_01.png do banco oficial.
Customize CARROSSEL_EXEMPLO e rode novamente — base padrao pra qualquer novo carrossel.

Para o exemplo REAL completo (referencia de 10 carrosseis publicados), ver:
    ../references/exemplo_real_carrosseis_mv.py
"""
from __future__ import annotations
from pathlib import Path

from carousel_design_system import (
    DOURADO_BRILHANTE, AMARELO_NEON, VERMELHO, TEAL_GLOW,
)
from templates import render_slide
from validador import validar_carrossel


CARROSSEL_EXEMPLO = {
    "tema": "Empresário ou refém?",
    "accent": AMARELO_NEON,
    "kicker_capa": "// PERGUNTA",
    "foto": "foto_01.png",  # arquivo em /opt/MAIA/assets/brand/banco_fotos/2026-05/
    "slides": [
        {
            "tipo": "capa",
            "headline": "EMPRESÁRIO OU REFÉM?",
            "cta": "ARRASTA",
        },
        {
            "tipo": "corpo",
            "headline": "TESTE BRUTAL",
            "body": [
                "Se tu sumir 7 dias,",
                "tua empresa para?",
                "Se para: tu não tem empresa.",
                "Tu tem um emprego com camisa de dono.",
            ],
        },
        {
            "tipo": "corpo",
            "headline": "EMPRESA DE VERDADE",
            "body": [
                "Roda sem o dono no operacional.",
                "Vendedor IA prospecta.",
                "WhatsApp IA qualifica.",
                "Tu cuida só do que ninguém mais pode: estratégia.",
            ],
        },
        {
            "tipo": "cta",
            "headline": "LINK NA BIO",
            "body": [
                "Imersão Máquina de Vendas com IA",
                "13 de junho — Online ao vivo",
                "Lote 1 Fundadores: R$47",
                "15 vagas",
            ],
        },
    ],
}


def main():
    problemas = validar_carrossel(CARROSSEL_EXEMPLO)
    if problemas:
        print("=== ALERTAS DO VALIDADOR ===")
        for p in problemas:
            print(p)
        print()
        # so derruba em erros estruturais; acentuacao vira warning
        erros_duros = [p for p in problemas if "[CARROSSEL]" in p or "tipo invalido" in p or "vazio" in p]
        if erros_duros:
            raise SystemExit("Erros estruturais impedem render.")

    out_dir = Path(__file__).parent / "out_exemplo"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = len(CARROSSEL_EXEMPLO["slides"])
    for i in range(1, total + 1):
        img = render_slide(CARROSSEL_EXEMPLO, i, total)
        out = out_dir / f"slide_{i}.png"
        img.save(out, "PNG", optimize=True)
        sz = out.stat().st_size // 1024
        print(f"  slide_{i}.png  {sz}KB  ({CARROSSEL_EXEMPLO['slides'][i-1]['tipo']})")
    print(f"\nOK. {total} slides em {out_dir}")


if __name__ == "__main__":
    main()
