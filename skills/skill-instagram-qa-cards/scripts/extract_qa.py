"""
Etapa 1: Extrai 10 pares de pergunta/resposta de uma transcricao usando Gemini.
"""
import os
import json
import argparse
from google import genai


def extract_qa_from_transcript(transcript_text: str, api_key: str) -> list:
    client = genai.Client(api_key=api_key)

    prompt = f"""Analise esta transcricao e extraia EXATAMENTE 10 pares de pergunta e resposta para posts de Instagram.

DISTRIBUICAO OBRIGATORIA (especifique o tipo de cada card):
- 3 dicas_praticas
- 2 mudancas_de_mentalidade
- 2 historias
- 2 insights_contraintuitivos
- 1 controverso

REGRAS DA PERGUNTA:
- Maximo 80 caracteres (conte os caracteres)
- Escreva como se um seguidor real escreveu: portugues coloquial, informal, sem pontuacao excessiva
- Exemplos de tom certo: "preciso saber programar pra isso?", "da pra fazer sem equipe?"

REGRAS DA RESPOSTA:
- Maximo 200 caracteres (conte os caracteres)
- Tom direto e energetico, como quem inspira empresarios a agir
- Identifique 2-3 palavras-chave importantes para destacar em negrito

REGRAS DA CATEGORIA:
- Rotulo curto que aparece acima da pergunta no sticker (maximo 25 caracteres)
- Exemplos: "automacao de negocio", "mentalidade", "IA na pratica"

Retorne APENAS JSON valido, sem markdown, sem explicacoes adicionais:
{{
  "cards": [
    {{
      "tipo": "dica_pratica",
      "categoria": "rotulo curto aqui",
      "pergunta": "texto da pergunta aqui",
      "resposta": "texto da resposta aqui",
      "destaques": ["palavra1", "palavra2", "palavra3"]
    }}
  ]
}}

TRANSCRICAO:
{transcript_text}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()
    # Remove markdown code block if present
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if part.strip().startswith("{") or part.strip().startswith("json\n{"):
                text = part.strip()
                if text.startswith("json"):
                    text = text[4:].strip()
                break

    data = json.loads(text)
    return data["cards"]


def main():
    parser = argparse.ArgumentParser(description="Extrai Q&A de transcricao usando Gemini")
    parser.add_argument("transcript", help="Caminho para o arquivo de transcricao (.txt)")
    parser.add_argument("--output", default="qa_cards.json", help="Arquivo de saida JSON")
    parser.add_argument("--api-key", default=os.environ.get("GOOGLE_API_KEY"))
    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("API key necessaria: use --api-key ou defina GOOGLE_API_KEY")

    with open(args.transcript, "r", encoding="utf-8") as f:
        transcript = f.read()

    print(f"Extraindo Q&A de: {args.transcript}")
    cards = extract_qa_from_transcript(transcript, args.api_key)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"cards": cards}, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(cards)} cards salvos em {args.output}")
    for i, card in enumerate(cards, 1):
        tipo = card.get("tipo", "?")
        pergunta = card.get("pergunta", "")[:55]
        print(f"  {i:02d}. [{tipo}] {pergunta}...")


if __name__ == "__main__":
    main()
