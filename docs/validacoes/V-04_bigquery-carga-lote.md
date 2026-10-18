# V-04 — Carga em lote gratuita no BigQuery

- **Status:** Concluída (2026-10-18) — leitura da página de preços; reconferir antes da primeira carga (M9)
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

- **Data:** 2026-10-18
- **Quem:** mentoria (Claude), com revisão pela pessoa desenvolvedora.
- **Fonte(s):**
  - `https://cloud.google.com/bigquery/pricing?hl=en`, acessada em 2026-10-18.
  - Resposta HTTP 200 com 4.838.328 bytes, SHA-256 `e7c7eb1293c3d71100a20d67911c56b9be2650d5d3d79c8d010ca108a1f0bb7c`.
  - A página veio inteira, ao contrário do que aconteceu no laboratório. Ela não mostra data de "última atualização". A cópia não foi guardada no repositório, por ser conteúdo de terceiros; os trechos literais estão abaixo.
- **O que foi feito:** leitura das seções "Free operations", "Data ingestion pricing" e "Free usage tier". Nenhuma conta foi criada e nada foi carregado.

Trechos literais (em inglês, como na página):

- **Free operations:** "The following BigQuery operations are free of charge in every location. Quotas and limits apply to these operations. [...] Batch load data — You are not charged for batch loading data using the shared slot pool. You can also create a reservation using editions pricing for guaranteed capacity. Once the data is loaded into BigQuery, you are charged for storage."
- **Data ingestion pricing:** "Batch Loading — Free using the shared slot pool named default-pipeline. Customers can choose editions pricing for guaranteed capacity. Once the data is loaded into BigQuery, you are charged for storage."
- **Free usage tier:** "These free usage limits are available during and after the free trial period. [...] Storage — The first 10 GiB per month is free. [...] Queries (analysis) — The first 1 TiB of query data processed per month is free."

## Resultado

**Não. A carga em lote não tem custo**, desde que use o pool compartilhado de slots (`default-pipeline`), que é o padrão. **Rótulo:** Fato (página oficial, 2026-10-18).

- **Fato:** o custo aparece depois, no armazenamento acima de 10 GiB por mês e nas consultas acima de 1 TiB processado por mês. Os dois limites valem durante e depois do período de teste, então se aplicam a uma conta com faturamento ativo.
- **Fato:** a página diz que "quotas and limits apply". Uma carga acima da cota é recusada, não cobrada.
- **Inferência:** o formato Parquet não muda a resposta. A página fala de carga em lote sem distinguir formato de arquivo.
- **Fora desta validação:** a cota diária e o alerta de orçamento, que a decisão exige antes da primeira carga, são configuração do M9, não leitura. Ficam como pré-requisito na lista do M9.

## Efeito no projeto

- A etapa B continua viável a custo zero, como a decisão supunha. Nada muda no plano.
- **Regras para o M9:**
  - carregar só por job de carga em lote, sem streaming (`Storage Write API`, cobrado por volume) e sem reserva de editions;
  - a decisão do M9 precisa registrar o tamanho esperado das tabelas (Inferência do CLAUDE.md: cerca de 1 GB por ano, bem abaixo dos 10 GiB).
- **`[VALIDAR]` no M9:** ler a página de cotas de carga (jobs por tabela e por projeto, por dia) antes de desenhar a frequência das cargas.
- **Reconferência obrigatória:** preços mudam. Antes da primeira carga, reler esta página e acrescentar aqui uma seção "Reconferência AAAA-MM-DD".
