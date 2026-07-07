"""
Etapa 3: Detecta o rosto na foto e retorna bounding box como proporcoes (0.0 a 1.0).
Usado para garantir que o texto nunca sobreponha o rosto.
"""
import argparse
import json
import sys
from pathlib import Path


DEFAULT_FACE_BOX = {"top": 0.05, "left": 0.15, "bottom": 0.48, "right": 0.85}


def detect_face(image_path: str) -> dict:
    """
    Retorna {"top": float, "left": float, "bottom": float, "right": float}
    como proporcoes de 0 a 1. Se nao detectar, usa posicao padrao segura.
    """
    try:
        import mediapipe as mp
        import numpy as np
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)

        mp_face = mp.solutions.face_detection
        with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.4) as detector:
            results = detector.process(image_np)
            if results.detections:
                det = results.detections[0]
                bb = det.location_data.relative_bounding_box
                face_box = {
                    "top": max(0.0, float(bb.ymin)),
                    "left": max(0.0, float(bb.xmin)),
                    "bottom": min(1.0, float(bb.ymin + bb.height)),
                    "right": min(1.0, float(bb.xmin + bb.width)),
                }
                print(f"  Rosto detectado: top={face_box['top']:.2f} bottom={face_box['bottom']:.2f}")
                return face_box

        print("  Aviso: rosto nao detectado, usando posicao padrao")
        return DEFAULT_FACE_BOX

    except ImportError:
        print("  Aviso: mediapipe nao instalado. Execute: pip install mediapipe")
        print("  Usando posicao padrao para o rosto")
        return DEFAULT_FACE_BOX
    except Exception as e:
        print(f"  Aviso: erro na deteccao de rosto ({e}), usando posicao padrao")
        return DEFAULT_FACE_BOX


def main():
    parser = argparse.ArgumentParser(description="Detecta rosto em uma imagem")
    parser.add_argument("image", help="Caminho da imagem")
    parser.add_argument("--output", help="Salvar resultado em arquivo JSON")
    args = parser.parse_args()

    result = detect_face(args.image)
    output_json = json.dumps(result, indent=2)
    print(output_json)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Salvo em: {args.output}")


if __name__ == "__main__":
    main()
