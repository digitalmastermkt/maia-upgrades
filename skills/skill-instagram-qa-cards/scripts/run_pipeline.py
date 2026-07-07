"""
Etapa 7: Pipeline completo — transcricao + fotos de referencia → 20 PNGs prontos.

Uso basico (com geracao de fotos por IA):
  python run_pipeline.py transcricao.txt --references foto1.jpg foto2.jpg --api-key SUA_CHAVE

Uso com foto fixa (sem gerar fotos por IA):
  python run_pipeline.py transcricao.txt --photo minha_foto.jpg --api-key SUA_CHAVE
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_qa import extract_qa_from_transcript
from detect_face import detect_face
from generate_photo import generate_photo, SCENE_PROMPTS
from compose_card import compose_card


def run_pipeline(
    transcript_path: str,
    api_key: str,
    output_dir: str = "output_cards",
    reference_photos: list = None,
    fixed_photo: str = None,
):
    """
    Pipeline completo: transcricao → 20 cards PNG (10 Q&A x 2 formatos).

    Se reference_photos e fornecido: gera fotos com IA (uma por card).
    Se fixed_photo e fornecido: usa a mesma foto como fundo de todos os cards.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    photos_dir = Path(output_dir) / "_fotos_geradas"

    use_ai_photos = bool(reference_photos) and not fixed_photo

    # ================================================================
    print("\n[1/4] Extraindo perguntas e respostas da transcricao...")
    # ================================================================
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    cards = extract_qa_from_transcript(transcript, api_key)

    qa_path = Path(output_dir) / "qa_cards.json"
    with open(qa_path, "w", encoding="utf-8") as f:
        json.dump({"cards": cards}, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(cards)} pares de Q&A salvos em {qa_path}")

    # ================================================================
    print("\n[2/4] Preparando fotos de fundo...")
    # ================================================================
    if use_ai_photos:
        photos_dir.mkdir(exist_ok=True)

    photo_face_pairs = []
    for i, card in enumerate(cards):
        if fixed_photo:
            photo_path = fixed_photo
        elif use_ai_photos:
            photo_path = str(photos_dir / f"photo_{i + 1:02d}.png")
            scene = SCENE_PROMPTS[i % len(SCENE_PROMPTS)]
            print(f"  Gerando foto {i + 1}/10 (cena: {scene[:45]}...)")
            try:
                generate_photo(reference_photos, scene, api_key, photo_path)
            except Exception as e:
                print(f"  ERRO gerando foto {i+1}: {e}")
                print(f"  Usando primeira foto de referencia como fallback")
                photo_path = reference_photos[0]
        else:
            photo_path = reference_photos[i % len(reference_photos)]

        face_box = detect_face(photo_path)
        photo_face_pairs.append((photo_path, face_box))

    # ================================================================
    print("\n[3/4] Compondo cards (sticker + resposta)...")
    # ================================================================
    output_files = []
    for i, (card, (photo_path, face_box)) in enumerate(zip(cards, photo_face_pairs), 1):
        for fmt in ["stories", "feed"]:
            out_name = f"card_{i:02d}_{fmt}.png"
            out_path = str(Path(output_dir) / out_name)
            print(f"  Card {i:02d} ({fmt}): {card.get('pergunta', '')[:50]}...")
            try:
                compose_card(photo_path, face_box, card, fmt, out_path)
                output_files.append(out_path)
            except Exception as e:
                print(f"  ERRO no card {i} {fmt}: {e}")

    # ================================================================
    print("\n[4/4] Resumo final")
    # ================================================================
    stories = [f for f in output_files if "stories" in f]
    feed = [f for f in output_files if "feed" in f]
    print(f"\n{'='*50}")
    print(f"CONCLUIDO: {len(output_files)} imagens geradas em '{output_dir}/'")
    print(f"  Stories (9:16): {len(stories)} imagens")
    print(f"  Feed    (4:5):  {len(feed)} imagens")
    print(f"  Q&A salvo em:   {qa_path}")
    print(f"{'='*50}\n")

    # Upload pro MinIO (nao-critico, falha silenciosa)
    minio_url = upload_cards_to_minio(output_dir, transcript_path)
    if minio_url:
        print(f"MinIO URL: {minio_url}")

    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline completo: transcricao → 20 cards Instagram prontos"
    )
    parser.add_argument("transcript", help="Arquivo de transcricao (.txt)")
    parser.add_argument(
        "--references", nargs="+",
        help="1 a 3 fotos suas de referencia para geracao com IA"
    )
    parser.add_argument(
        "--photo",
        help="Usar uma foto fixa como fundo (sem gerar com IA)"
    )
    parser.add_argument(
        "--output", default="output_cards",
        help="Diretorio de saida (default: output_cards)"
    )
    parser.add_argument(
        "--api-key", default=os.environ.get("GOOGLE_API_KEY"),
        help="Chave da API Google (ou defina GOOGLE_API_KEY)"
    )
    args = parser.parse_args()

    if not args.api_key:
        print("ERRO: API key necessaria.")
        print("Use --api-key SUA_CHAVE ou defina: set GOOGLE_API_KEY=SUA_CHAVE")
        sys.exit(1)

    if not args.references and not args.photo:
        print("ERRO: Forneca --references (fotos para IA gerar) ou --photo (foto fixa).")
        sys.exit(1)

    run_pipeline(
        transcript_path=args.transcript,
        api_key=args.api_key,
        output_dir=args.output,
        reference_photos=args.references,
        fixed_photo=args.photo,
    )


def _slugify(text: str) -> str:
    import unicodedata, re
    nfd = unicodedata.normalize('NFD', text)
    no_marks = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    no_marks = no_marks.lower()
    no_marks = re.sub(r'[^a-z0-9]+', '-', no_marks).strip('-')
    return no_marks or 'sem-nome'


def _load_minio_env():
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv('/opt/MAIA/bot/.env')
    except Exception:
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


def upload_cards_to_minio(output_dir: str, transcricao_filename: str) -> str:
    """
    Faz upload de todos PNGs em output_dir para naia-entregas/cards-instagram/YYYY-MM-DD-slug/
    Retorna URL do console MinIO ou string vazia se falhar (nao levanta excecao).
    """
    try:
        import boto3
        from datetime import date
        from pathlib import Path
        env = _load_minio_env()
        if not env['endpoint'] or not env['access_key']:
            print("[MinIO] Sem credenciais no .env, pulando upload")
            return ""
        slug = _slugify(Path(transcricao_filename).stem)
        prefix = f"cards-instagram/{date.today().isoformat()}-{slug}"
        client = boto3.client(
            's3',
            endpoint_url=env['endpoint'],
            aws_access_key_id=env['access_key'],
            aws_secret_access_key=env['secret_key'],
        )
        out = Path(output_dir)
        count = 0
        for png in out.glob('*.png'):
            client.upload_file(str(png), env['bucket'], f"{prefix}/{png.name}")
            count += 1
        url = f"{env['console']}/browser/{env['bucket']}/{prefix.replace('/', '%2F')}%2F"
        print(f"[MinIO] Upload OK: {count} PNGs -> {url}")
        return url
    except Exception as e:
        print(f"[MinIO] Upload FALHOU (nao-critico): {e}")
        return ""


if __name__ == "__main__":
    main()
