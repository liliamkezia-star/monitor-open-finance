# Origem do projeto

Este projeto foi escolhido num laboratório de pesquisa de portfólio (fases 01 a 07), com evidência rastreável. Este documento resume a escolha; a fonte completa é o laboratório (arquivos citados abaixo, todos de 2026-10-08).

Fontes principais:
- Decisão: `07_projeto_final/2026-10-08_decisao.md`
- Verificação de custo zero: `07_projeto_final/2026-10-08_anexo_custo-zero.md`
- Ficha da oportunidade #16 e checagem regulatória: `06_oportunidades/2026-10-08_oportunidades.md`, ficha #16 e seção 7.4

## 1. A escolha

- **Projeto escolhido:** #16, "Monitor externo do Manual 3.0 do Open Finance" (fusão de um validador de conformidade com um observatório de disponibilidade). Decisão de 2026-10-08. Fato.
- **Top 3 apresentado:** #3 (avaliação de IA que reage a dados novos, ANP), #16 e #1 (gate de CI para agente sobre o Pix). Notas compostas 4,70 · 4,65 · 4,55; o #16 foi 1º com pesos iguais (4,75) e com pesos invertidos (4,85). Ranking declarado frágil; na prática, a escolha era #3 × #16. Evidência.
- **Porquê de quem decidiu (Opinião, registrada na decisão):** o portfólio atual já prova IA; o que falta provar e aparece nas vagas é orquestração, cloud fora da Microsoft e operação contínua, num problema real e brasileiro, medido ao vivo, sem colar IA para não cair em technology soup.

Ressalvas registradas na própria decisão:
- Orquestração é um gap transversal, mas não "o que mais aparece" nas vagas (Databricks aparece em mais). Evidência.
- "Operação contínua" não foi medida como requisito; o mais próximo é observabilidade, sinal emergente. Evidência / Inferência.
- "0/18 portfólios pares fazem Open Finance" significa "não encontrado nos materiais lidos", não inexistência. Evidência.

## 2. O problema

- O Manual de APIs 7.0 (IN BCB 615/2025) fixa, para endpoints de **Dados Abertos**, disponibilidade diária ≥ 95% e longa (90 dias) ≥ 99,5% (5.4.2) e p95 diário de 1.500 a 4.000 ms conforme a classe de frequência (5.3.2). Fato.
- O Manual de Monitoramento 3.0 (IN BCB 706/2026) monitora esses itens (2.1) e a aderência às especificações (2.2, II, a). Fato.
- A Res. BCB 32/2020, art. 5º, exige acesso público a dados "permanentemente atualizados". Fato.
- Para disponibilidade, vale "o valor reportado pelo consumidor da API" (IN 615, 5.4.2, IV) — exatamente o ponto de vista de um monitor externo. Fato.
- Quem usaria (Inferência, da ficha #16): comparadores e fintechs que consomem os dados; times das participantes; imprensa especializada e pesquisadores.

Detalhes e trechos literais: `docs/normas/sla.md`.

## 3. O que o projeto prova e não prova

Ver CLAUDE.md, seção 2. Em resumo: estima disponibilidade, p95 e conformidade **do ponto de vista do consumidor**; não mede a métrica oficial, o índice de qualidade de dados (fora do escopo, IN 706, item V), as APIs autenticadas nem o HTTP 529 de forma ativa.

## 4. Arquitetura A → B

### Etapa A — MVP

- **VM Oracle Always Free** (Ampere A1, 2 OCPUs / 12 GB), região de origem **São Paulo ou Vinhedo** (V-01). Medir do Brasil é a correção principal do viés de latência.
- **Airflow** na VM (condicionado à V-01): DAG de medição a cada 15 minutos; DAG diária com dependências e prazo até as 8h.
- **Postgres ou DuckDB** no Block Volume (decisão no M2).
- **Parquet diário como contrato** entre coleta e análise; a etapa B lê o mesmo contrato, sem refazer a coleta.
- **dbt**: as regras do Manual viram modelos testados.
- **GitHub Actions só para CI e publicação do site estático; nunca para coleta** (V-08).
- **Escopo do MVP:** 3 famílias de Dados Abertos (empréstimos, contas, cartões), todas as instituições do Diretório, **4 semanas de medição**; disponibilidade, p95, conformidade com o schema e versões antigas.
- **Volume:** ~154 endpoints × 96 medições por dia ≈ 1,5 × 10⁴ medições por dia (correção da decisão; a ficha dizia ~10⁵). Fato (cálculo) sobre contagem do Diretório de 2026-10-08.

### Etapa B — evolução

- **Gatilho:** etapa A estável por cerca de 2 semanas (M8).
- Carga dos Parquet no **BigQuery** (free tier, com conta de faturamento) e **Looker Studio** como painel. Cota diária e alerta de orçamento **antes** da primeira carga. O sandbox sem cartão não serve (expiração de 60 dias × janela de 90).
- **Justificativa honesta:** o BigQuery entra para fechar o gap de cloud fora da Microsoft (G5), **não pela escala** (~1 GB por ano, Inferência). O README declara isso.

### O que a etapa A não fecha

- **G5 (cloud fora da Microsoft) não fecha na etapa A:** Oracle não é AWS nem GCP. Fecha só na etapa B. Evidência / Inferência (decisão, seção 3).
- Por isso, a aderência a vagas de Analytics Engineer é **11/15 (73%)** na etapa A e **12/15 (80%)** com a etapa B. Evidência (decisão, correção de 2026-10-08).

## 5. Viés de latência e método

Fato (IN 615, 5.3 e 5.3.2, V): o provedor mede do gateway até o envio do último byte; o consumidor mede de antes da requisição até o último byte recebido — a medida do consumidor inclui a rede.

Correção adotada (Inferência, método do anexo de custo zero, seção 5):
1. medir do Brasil;
2. separar as fases de tempo da requisição e publicar o **p95 total** e o **p95 sem a rede**;
3. usar um **endpoint de controle** para calibrar a rede;
4. **rotular a origem** em todas as medições;
5. nunca afirmar violação de SLA; só "estimativa externa acima do limite de referência".

Frequência inicial: **1 requisição a cada 15 minutos por endpoint**; a métrica oficial usa todas as requisições de cada minuto, então o resultado é uma estimativa, com intervalo de confiança declarado (M5).

## 6. Riscos herdados da decisão

| Risco | Onde é tratado |
|---|---|
| A1 indisponível em São Paulo/Vinhedo; "out of host capacity" | V-01 |
| Bloqueio de IP estrangeiro | V-02 |
| Termos do Diretório/Portal e limites por IP | V-03 |
| Carga em lote gratuita no BigQuery | V-04 |
| Recuperação por ociosidade (CPU, rede e memória < 20% por 7 dias) e conta abandonada após 30 dias sem acesso | Manual de operação (M3) |
| Cartão de crédito exigido (Oracle; Google na etapa B) | V-01, V-04 |
| Medição amostral × métrica oficial | CLAUDE.md, seções 2 e 4; M5 |
| Sem IA: não é a ponte para AI Engineer (a ponte fica com o portfólio existente) | Decisão, seção 3 — aceito |
