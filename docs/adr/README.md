# Registros de decisão de arquitetura (ADR)

Toda decisão técnica relevante fica registrada aqui, com a fonte que a sustenta (CLAUDE.md, seção 9; skill `adr`).

## Índice

| ADR | Título | Status | Data |
|---|---|---|---|
| [ADR-001](ADR-001-medir-do-brasil-caminho-a-b.md) | Medir do Brasil e caminho A → B | Em redação | — |

ADRs já previstos (ainda não abertos):
- M1: frequência de coleta (valor inicial: 1 requisição a cada 15 minutos por endpoint; depende da V-03).
- M1: dois indicadores separados — disponibilidade pelo status code (IN 615, 5.4.1) e conformidade pelo corpo; tratamento de falhas sem status code.
- M1: timeout do coletor (base: IN 615, 5.5, 15 s).
- M4: orquestrador (Airflow, condicionado à V-01).

## Regras

- Numeração sequencial, nunca reaproveitada. Nome do arquivo: `ADR-NNN-titulo-em-kebab-case.md`.
- Status: **Proposto** → **Aceito** → (**Substituído por ADR-NNN** | **Descartado**).
- Um ADR aceito não é reescrito. Uma mudança gera um ADR novo que o substitui; o antigo ganha só a linha de status.
- Toda afirmação factual tem fonte e data; afirmações relevantes levam rótulo (Fato, Evidência, Inferência, Opinião, Hipótese).

## Modelo

```markdown
# ADR-NNN — <título>

- **Status:** Proposto | Aceito | Substituído por ADR-NNN | Descartado
- **Data:** AAAA-MM-DD
- **Marco:** M?
- **Depende de:** <validações, outros ADRs>

## Contexto
<o problema concreto que obriga a decidir agora; restrições; o que a norma diz (com item)>

## Decisão
<o que foi decidido, em uma ou duas frases>

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| ... | ... |

## Consequências
- **Positivas:** ...
- **Negativas (obrigatório):** ...
- **O que muda no projeto:** <código, docs, marcos>

## Gatilho de revisão
<o que faria esta decisão ser reaberta>

## Fontes
| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| ... | ... | ... | ... |
```
