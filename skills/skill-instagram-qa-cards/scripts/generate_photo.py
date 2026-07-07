"""
Etapa 2: Gera fotos com IA usando Gemini, preservando o rosto/identidade
a partir de fotos de referencia fornecidas pelo usuario.

Nota: O Gemini 2.0 Flash faz um bom trabalho de consistencia facial mas
resultados podem variar. Se a foto gerada nao estiver boa, rode novamente
ou use --scene para variar o cenario.
"""
import os
import argparse
import base64
from pathlib import Path
from google import genai
from google.genai import types


SCENE_PROMPTS = [
    "Selfie casual dentro de um carro, assento do motorista, janela ao fundo com paisagem urbana. Expressao confiante e sorridente. Luz natural pela janela.",
    "Selfie em ambiente de escritorio moderno, fundo levemente desfocado com plantas. Expressao focada e profissional. Iluminacao de janela lateral.",
    "Foto em ambiente externo urbano, calcada com lojas ao fundo desfocado. Expressao descontraida e feliz. Luz do sol suave.",
    "Selfie em cafe ou coworking, mesa ao fundo com notebook, xicara de cafe. Expressao animada. Iluminacao aconchegante.",
    "Foto em sala de estar moderna, sofa claro ao fundo, quadros na parede. Postura relaxada e confiante. Luz natural de janela.",
    "Selfie em frente a janela grande com vista de cidade. Expressao determinada. Contra-luz suave criando halo no cabelo.",
    "Foto em corredor de hotel ou escritorio moderno, fundo limpo e elegante. Expressao de quem acabou de ter uma ideia incrivel.",
    "Selfie em ambiente ao ar livre, parque ou jardim ao fundo. Expressao leve e descontraida. Sombra filtrada pelas arvores.",
    "Foto em academia ou espaco de bem-estar, equipamentos ao fundo desfocados. Expressao energica e motivada.",
    "Selfie em evento ou palco, luzes ao fundo desfocadas. Expressao de quem esta prestes a subir no palco. Energia alta.",
]


def generate_photo(reference_photos: list, scene_prompt: str, api_key: str, output_path: str) -> str:
    client = genai.Client(api_key=api_key)

    contents = []

    for photo_path in reference_photos:
        with open(photo_path, "rb") as f:
            image_bytes = f.read()
        ext = Path(photo_path).suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime))

    prompt_text = f"""Estas sao fotos de referencia da mesma pessoa. Gere uma NOVA foto realista dela.

CENA: {scene_prompt}

REQUISITOS OBRIGATORIOS:
- Preserve EXATAMENTE o rosto, feicoes, maquiagem e caracteristicas da pessoa das fotos de referencia
- Estilo foto de celular casual — NAO parece foto de estudio ou profissional
- Pele REAL com poros visiveis, linhas de expressao naturais
- Cabelo com textura real, frizz natural se houver
- Corpo e proporcoes IDENTICOS — NUNCA emagrecer, alterar shape ou aparencia fisica
- Iluminacao natural ou de ambiente (nao flash artificial)
- Formato vertical (retrato), alta resolucao
- A pessoa deve estar claramente visivel no centro/superior da imagem

NAO altere nenhuma caracteristica fisica. A identidade visual deve ser identica."""

    contents.append(prompt_text)

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            image_data = part.inline_data.data
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"  OK foto gerada: {output_path}")
            return output_path

    raise RuntimeError(
        "Gemini nao retornou imagem. Verifique o modelo disponivel na sua conta do Google AI Studio."
    )


def main():
    parser = argparse.ArgumentParser(description="Gera fotos com IA usando Gemini")
    parser.add_argument("references", nargs="+", help="1 a 3 fotos de referencia da pessoa (.jpg ou .png)")
    parser.add_argument("--output-dir", default="generated_photos", help="Diretorio de saida (default: generated_photos)")
    parser.add_argument("--count", type=int, default=10, help="Quantas fotos gerar (default: 10)")
    parser.add_argument("--scene", help="Descricao customizada da cena (opcional)")
    parser.add_argument("--api-key", default=os.environ.get("GOOGLE_API_KEY"))
    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("API key necessaria: use --api-key ou defina GOOGLE_API_KEY")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    generated = []

    for i in range(args.count):
        scene = args.scene or SCENE_PROMPTS[i % len(SCENE_PROMPTS)]
        output_path = str(Path(args.output_dir) / f"photo_{i + 1:02d}.png")
        print(f"Gerando foto {i + 1}/{args.count}...")
        try:
            path = generate_photo(args.references, scene, args.api_key, output_path)
            generated.append(path)
        except Exception as e:
            print(f"  ERRO na foto {i + 1}: {e}")

    print(f"\nTotal: {len(generated)}/{args.count} fotos geradas em '{args.output_dir}/'")


if __name__ == "__main__":
    main()
