# V-04 — Carga em lote gratuita no BigQuery

- **Status:** Pendente
- **Prioridade:** Baixa (etapa B); obrigatória antes da primeira carga
- **Etapa / marco afetado:** B; M9
- **Origem da pendência:** laboratório, anexo de custo zero, seção 3 (a página de preços veio truncada)

## Pergunta

Carregar arquivos Parquet no BigQuery por job de carga em lote tem custo, dentro de uma conta com faturamento ativo e uso no free tier?

## Por que importa

- A etapa B só é custo zero se a carga em lote, o armazenamento (≤ 10 GiB) e as consultas (≤ 1 TiB/mês) ficarem no free tier.
- O sandbox sem cartão não serve: tabelas e partições expiram em 60 dias e o SLA usa janela de 90 (Fato, anexo, seção 3).

## Como verificar

- Ler a página oficial de preços do BigQuery (`cloud.google.com/bigquery/pricing`), seção de ingestão/carga, guardando trecho literal e data.
- Conferir também o que a decisão exige antes da primeira carga: cota diária e alerta de orçamento configurados.

## Execução

- **Data:**
- **Quem:**
- **Fonte(s):**
- **O que foi feito:**

## Resultado

—

## Efeito no projeto

—
