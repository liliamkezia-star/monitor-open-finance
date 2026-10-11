# V-06 — Classe de frequência de cada endpoint de Dados Abertos

- **Status:** Pendente
- **Prioridade:** Média (antes do M5; idealmente junto com a V-03)
- **Etapa / marco afetado:** A; M5 (p95 por classe)
- **Origem da pendência:** laboratório, oportunidades, seção 8

## Pergunta

Em qual classe de frequência (alta, média-alta, média, baixa) cada endpoint de Dados Abertos das famílias do MVP está classificado no Portal do Open Finance?

## Por que importa

- O limite de p95 depende da classe: 1.500, 2.000 ou 4.000 ms (IN 615, 5.3.2, I a III; `docs/normas/sla.md`, seção 2).
- A IN 615, seção 5, diz que "é necessário que cada endpoint seja classificado no Portal do Open Finance" (Fato, texto de `in615.txt`).
- Sem a classe, o projeto publica o p95 mas não o compara com nenhum limite.

## Como verificar

- Localizar no Portal a tabela de classificação; guardar URL, data e a tabela (ou trecho) usada.
- Registrar a classe por endpoint e versão, para uso como semente (seed) no dbt no M5.

## Execução

- **Data:**
- **Quem:**
- **Fonte(s):**
- **O que foi feito:**

## Resultado

—

## Efeito no projeto

—
