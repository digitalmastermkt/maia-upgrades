# Templates de Prompt — Instagram Q&A Cards

## Prompt de Extracao de Q&A (extract_qa.py)

Instrucoes chave enviadas ao Gemini Flash:

### Distribuicao obrigatoria dos 10 cards:
- 3 dicas_praticas
- 2 mudancas_de_mentalidade
- 2 historias
- 2 insights_contraintuitivos
- 1 controverso

### Criterios de qualidade da pergunta:
- Maximo 80 caracteres (conte antes de gerar)
- Tom de seguidor real: informal, coloquial, sem pontuacao excessiva
- Evitar: "Como posso...?", "Qual e a melhor forma...?"
- Preferir: "da pra fazer isso sem equipe?", "precisa de dinheiro pra comecar?"

### Criterios de qualidade da resposta:
- Maximo 200 caracteres
- Tom alinhado a voz da marca (ver /opt/MAIA/brand/brand.json)
- Usar o slogan da marca quando natural (slogan_or_blank() do brand_loader)
- 2-3 palavras-chave identificadas para destaque em negrito
- Nunca prometer resultado sem esforco

### Formato de saida esperado (JSON):
```json
{
  "cards": [
    {
      "tipo": "dica_pratica",
      "categoria": "automacao de negocio",
      "pergunta": "da pra automatizar sem saber programar?",
      "resposta": "Sim. Ferramentas de IA hoje nao exigem codigo. Exigem clareza do processo. Automatize o que voce ja faz bem.",
      "destaques": ["clareza", "processo"]
    }
  ]
}
```

## Prompts de Geracao de Foto (generate_photo.py)

### Requisitos invariaveis (sempre incluir):
- Preservar EXATAMENTE o rosto, feicoes, maquiagem das fotos de referencia
- Estilo foto de celular casual (nao estudio, nao profissional)
- Pele REAL com poros, linhas de expressao naturais
- Corpo e proporcoes identicos — NUNCA alterar fisicamente
- Formato vertical (retrato), alta resolucao
- Pessoa visivel no centro/superior da imagem

### Os 10 cenarios rotativos pre-definidos:
1. Selfie casual em carro — assento motorista, janela com paisagem urbana
2. Escritorio moderno — fundo com plantas, iluminacao de janela
3. Ambiente externo urbano — calcada, fundo desfocado
4. Cafe ou coworking — mesa com notebook ao fundo
5. Sala de estar moderna — sofa claro, luz natural
6. Frente a janela grande — vista de cidade, contra-luz suave
7. Corredor de hotel/escritorio — fundo limpo e elegante
8. Area externa — parque ou jardim, sombra filtrada
9. Academia ou espaco de bem-estar — energia alta
10. Palco ou evento — luzes ao fundo desfocadas

### Modelo Gemini para geracao de imagens:
- Modelo: `gemini-2.0-flash-preview-image-generation`
- response_modalities: ["IMAGE", "TEXT"]
- Enviar 1-3 fotos de referencia + prompt textual na mesma requisicao

## Ajustes Possiveis

Se o Gemini retornar erro no modelo de geracao de imagens:
1. Verificar qual modelo de imagens esta disponivel no Google AI Studio
2. Testar: `gemini-2.0-flash-exp-image-generation` como alternativa
3. Se nenhum funcionar, usar `--photo` com foto manual no run_pipeline.py

Se as fotos geradas nao preservarem bem o rosto:
1. Fornecer mais fotos de referencia (3 e ideal, diferentes angulos)
2. Adicionar descricao fisica mais detalhada ao prompt
3. Gerar varias vezes e selecionar a melhor manualmente
