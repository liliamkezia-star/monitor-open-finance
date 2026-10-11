---
name: adr
description: Mentoria para escrever um ADR (registro de decisão de arquitetura) deste projeto. Use quando surgir uma decisão técnica relevante, quando a pessoa pedir para escrever ou revisar um ADR, ou quando uma ferramenta nova for proposta.
---

# ADR

A pessoa desenvolvedora escreve o ADR. Claude orienta com dicas em níveis (skill `sessao-desenvolvimento`, seção 2) e revisa.

## Quando precisa de ADR

- Ferramenta, serviço ou dependência nova (CLAUDE.md, seção 9).
- Decisão de método que muda um número publicado (frequência, critério de disponibilidade, cálculo do p95, intervalo de confiança).
- Mudança de arquitetura ou de plano (ex.: V-01 falhar e o Airflow ser substituído).

## Arquivo

- `docs/adr/ADR-NNN-titulo-em-kebab-case.md`, numeração sequencial, nunca reaproveitada.
- Atualizar o índice em `docs/adr/README.md`.
- Modelo: `docs/adr/README.md`, seção "Modelo".

## Perguntas de mentoria (nível 1), uma por vez

1. Qual problema concreto obriga a decidir agora?
2. Quais alternativas foram consideradas, incluindo "não fazer nada"?
3. Que fonte sustenta cada afirmação? (norma com item, documentação oficial com data, registro de validação)
4. Qual rótulo cada afirmação leva: Fato, Evidência, Inferência, Opinião ou Hipótese?
5. O que fica pior com esta decisão? (consequências negativas são obrigatórias)
6. O que faria esta decisão ser revista? (gatilho de revisão)

## Revisão do ADR pronto

- Toda afirmação factual tem fonte e data; nenhuma fonte citada sem ter sido lida.
- Alternativas descartadas têm motivo.
- Rótulos presentes e coerentes (uma Inferência não está escrita como Fato).
- Status coerente: Proposto → Aceito → (Substituído por ADR-NNN). Um ADR aceito não é reescrito: uma mudança gera um novo ADR que o substitui.
- Se depende de uma validação pendente, diz isso e fica "Proposto".
