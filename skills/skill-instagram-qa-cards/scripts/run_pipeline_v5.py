"""
run_pipeline_v5.py - Pipeline final v3 (5 Q&A, arquitetura capa+4P+4R+CTA).

Loop:
  1. Le transcricao + extrai 5 QAs (cache compatible com qa_cards.json existente).
  2. STORIES: 5 cards com Q+A juntos (1080x1920).
  3. FEED: 10 cards no carrossel (capa + 4P + 4R + CTA, 1080x1350).
  4. Upload MinIO em naia-entregas/cards-instagram/<DATA>-<SLUG>-v3-arquitetura-correta/

Total: 15 PNGs.
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compose_card_v5 import (
    compose_stories_qa, compose_feed_pergunta, compose_feed_resposta,
    compose_feed_capa, compose_feed_cta, save_png,
)


# Placeholders (ajustar conforme a edicao)
TITULO_IMERSAO = "IMERSAO IA NA PRATICA"
DATA_EDICAO = "06.06.2026 - SABADO"
TAGLINE = "5 perguntas que tu precisa fazer antes de aplicar IA no teu negocio"
LINK_BIO_TEXT = "Link na bio pra garantir vaga"


def load_qa_cards(qa_cards_json):
    with open(qa_cards_json, encoding="utf-8") as f:
        data = json.load(f)
    cards = data.get("cards", [])
    if len(cards) < 5:
        raise SystemExit(f"qa_cards.json tem so {len(cards)} cards, precisa de 5")
    return cards[:5]


def listar_banco(banco_dir):
    """Lista PNGs/JPGs do banco em ordem alfabetica."""
    p = Path(banco_dir)
    fotos = []
    for ext in ("*.png", "*.jpg"):
        fotos.extend(sorted(p.glob(ext)))
    # Filtra .old/.bak/_backup
    fotos = [str(f) for f in fotos if not any(k in f.name for k in (".old", ".bak", "backup"))]
    if not fotos:
        raise SystemExit(f"Sem fotos em {banco_dir}")
    return fotos


def run_pipeline_v5(qa_cards_json, banco_dir, output_dir,
                    titulo=TITULO_IMERSAO, data=DATA_EDICAO,
                    tagline=TAGLINE, link_bio=LINK_BIO_TEXT):
    out = Path(output_dir)
    stories_dir = out / "stories"
    feed_dir = out / "feed"
    stories_dir.mkdir(parents=True, exist_ok=True)
    feed_dir.mkdir(parents=True, exist_ok=True)

    qa_list = load_qa_cards(qa_cards_json)
    banco = listar_banco(banco_dir)
    print(f"Q&As: {len(qa_list)} | Fotos: {len(banco)}")

    # ============== STORIES (5 cards) ==============
    print("\n[1/2] STORIES (5 cards 1080x1920 Q+A juntos)...")
    for i, qa in enumerate(qa_list, 1):
        foto = banco[(i - 1) % len(banco)]
        canvas = compose_stories_qa(
            pergunta=qa.get("pergunta", ""),
            resposta=qa.get("resposta", ""),
            destaques=qa.get("destaques", []),
            foto_path=foto,
            num_q=i,
            total_q=5,
        )
        save_png(canvas, str(stories_dir / f"stories_{i:02d}.png"))

    # ============== FEED (10 cards = carrossel) ==============
    print("\n[2/2] FEED (10 cards 1080x1350 = capa + 4P + 4R + CTA)...")

    # 01 capa
    canvas = compose_feed_capa(titulo, data, tagline)
    save_png(canvas, str(feed_dir / "feed_01_capa.png"))

    # 02-09: 4 perguntas + 4 respostas alternadas (so primeiras 4 QAs)
    for i, qa in enumerate(qa_list[:4], 1):
        foto = banco[(i - 1) % len(banco)]
        # Pergunta posicao 2,4,6,8
        canvas = compose_feed_pergunta(
            pergunta=qa.get("pergunta", ""),
            foto_path=foto,
            num_q=i,
            total_q=4,
        )
        save_png(canvas, str(feed_dir / f"feed_{2*i:02d}_pergunta.png"))
        # Resposta posicao 3,5,7,9
        canvas = compose_feed_resposta(
            resposta=qa.get("resposta", ""),
            destaques=qa.get("destaques", []),
            foto_path=foto,
            num_q=i,
            total_q=4,
        )
        save_png(canvas, str(feed_dir / f"feed_{2*i+1:02d}_resposta.png"))

    # 10 CTA - passa data completa ("06.06.2026 - SABADO") conforme decisao
    canvas = compose_feed_cta(titulo, data, link_bio)
    save_png(canvas, str(feed_dir / "feed_10_cta.png"))

    # =================== Resumo ===================
    stories_files = sorted(stories_dir.glob("*.png"))
    feed_files = sorted(feed_dir.glob("*.png"))
    print(f"\n{'='*60}")
    print(f"OK: {len(stories_files)} stories + {len(feed_files)} feed = {len(stories_files) + len(feed_files)} PNGs")
    print(f"  stories: {stories_dir}")
    print(f"  feed:    {feed_dir}")
    print(f"{'='*60}\n")

    return stories_files, feed_files


# ====== MinIO upload =========================================
def _slugify(text):
    import unicodedata, re
    nfd = unicodedata.normalize('NFD', text)
    no_marks = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    no_marks = no_marks.lower()
    no_marks = re.sub(r'[^a-z0-9]+', '-', no_marks).strip('-')
    return no_marks or 'sem-nome'


def _load_minio_env():
    env_file = '/opt/MAIA/bot/.env'
    if os.path.exists(env_file):
        with open(env_file) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return {
        'endpoint': os.getenv('MINIO_ENDPOINT'),
        'access_key': os.getenv('MINIO_ACCESS_KEY'),
        'secret_key': os.getenv('MINIO_SECRET_KEY'),
        'bucket': os.getenv('MINIO_BUCKET', 'naia-entregas'),
        'console': os.getenv('MINIO_CONSOLE_URL', 'http://localhost:9001'),
    }


def upload_v3_to_minio(output_dir, custom_prefix):
    """Upload TUDO de output_dir/stories e output_dir/feed pra MinIO sob custom_prefix."""
    try:
        import boto3
        env = _load_minio_env()
        if not env['endpoint'] or not env['access_key']:
            print("[MinIO] Sem credenciais no .env, pulando upload")
            return ""
        client = boto3.client(
            's3',
            endpoint_url=env['endpoint'],
            aws_access_key_id=env['access_key'],
            aws_secret_access_key=env['secret_key'],
        )
        prefix = f"cards-instagram/{custom_prefix}"
        out = Path(output_dir)
        count = 0
        for sub in ("stories", "feed"):
            sub_dir = out / sub
            for png in sorted(sub_dir.glob("*.png")):
                key = f"{prefix}/{sub}/{png.name}"
                client.upload_file(str(png), env['bucket'], key)
                count += 1
        url = f"{env['console']}/browser/{env['bucket']}/{prefix.replace('/', '%2F')}%2F"
        print(f"[MinIO] Upload OK: {count} PNGs -> {url}")
        return url
    except Exception as e:
        print(f"[MinIO] Upload FALHOU (nao-critico): {e}")
        return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa-cards", required=True, help="qa_cards.json com >= 5 QAs")
    parser.add_argument("--banco", required=True, help="Diretorio com fotos")
    parser.add_argument("--output", required=True, help="Diretorio output (ex /tmp/cards-aula3-v3)")
    parser.add_argument("--prefix", default=None, help="Prefix MinIO (default: data-slug-v3-arquitetura-correta)")
    parser.add_argument("--titulo", default=TITULO_IMERSAO)
    parser.add_argument("--data", default=DATA_EDICAO)
    parser.add_argument("--tagline", default=TAGLINE)
    parser.add_argument("--link-bio", default=LINK_BIO_TEXT)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--slug-base", default="aula-3", help="usado no prefix MinIO se nao fornecido")
    args = parser.parse_args()

    run_pipeline_v5(
        qa_cards_json=args.qa_cards,
        banco_dir=args.banco,
        output_dir=args.output,
        titulo=args.titulo,
        data=args.data,
        tagline=args.tagline,
        link_bio=args.link_bio,
    )

    if args.upload:
        from datetime import date
        prefix = args.prefix or f"{date.today().isoformat()}-{args.slug_base}-v3-arquitetura-correta"
        url = upload_v3_to_minio(args.output, prefix)
        if url:
            print(f"\n>>> URL MinIO: {url}")


if __name__ == "__main__":
    main()
