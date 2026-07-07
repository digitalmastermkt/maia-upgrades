# skill-persona-profunda

Skill do Claude Code que gera personas completas com **30 dimensões psicológicas profundas** + Buyer Persona + ICP (Ideal Customer Profile) + Mapa de Empatia + Anti-Persona.

Produz perfis ultradetalhados com 10 elementos por dimensão (300+ insights) para uso em copy, lançamentos, anúncios e estratégia de produto.

Criada por [Tata Gonçalves](https://mentoriaimperioia.com) — parte do ecossistema Mentoria Império IA.

---

## O que ela faz

Quando você invoca `/skill-persona-profunda` no Claude Code, ela ativa 5 fluxos:

1. **Persona Profunda Completa** — 30 dimensões psicológicas (medos, desejos, crenças, identidade, jornada, gatilhos, objeções, vocabulário, rotina, etc.)
2. **Buyer Persona Estratégica** — perfil completo para copy e funil
3. **ICP (Ideal Customer Profile)** — quem é o cliente ideal pra prospectar
4. **Mapa de Empatia Expandido** — o que pensa, sente, vê, ouve, fala e faz
5. **Anti-Persona** — quem NÃO é seu cliente (filtro de qualificação)

## Como instalar

No terminal:

```bash
cd ~/.claude/skills/
git clone https://github.com/tatagoncalvesof/skill-persona-profunda.git
```

Pronto. Reinicie o Claude Code e a skill `/skill-persona-profunda` aparece disponível.

## Como usar

Dentro do Claude Code, basta pedir:

- `/skill-persona-profunda` — menu completo
- "cria uma persona profunda pra meu produto X"
- "monta o buyer persona da minha mentoria"
- "quero o ICP do meu serviço"
- "faz o mapa de empatia do meu público"
- "quem NÃO é meu cliente?" (anti-persona)

A skill faz perguntas de descoberta e devolve o perfil estruturado pronto pra usar em copy, anúncios, headlines, mecanismo único, e-mail, VSL.

## Estrutura

```
skill-persona-profunda/
├── SKILL.md                        # arquivo principal da skill
└── references/
    ├── dimensoes-psicologicas.md   # 30 dimensões detalhadas
    ├── buyer-persona-framework.md  # framework Buyer Persona
    ├── icp-framework.md            # framework ICP
    └── aplicacao-em-copy.md        # como aplicar a persona em copy
```

## Integra com

Outras skills do ecossistema Império IA:

- `/briefing-copy-360` — usa a persona como input de briefing
- `/headline-imperatriz` — gera headlines a partir das dores/desejos da persona
- `/mecanismo-unico` — constrói o mecanismo a partir do vilão da persona
- `/copywriting` — escreve copy mirado nessa persona
- `/skill-pagina-vendas` — gera página de vendas usando o perfil

## Licença

MIT — use, modifique, distribua. Apenas mantenha o crédito.
