# ADR-001 — Medir do Brasil e caminho A → B

- **Status:** Aceito
- **Data:** 2026-10-29
- **Marco:** M0
- **Depende de:** V-01 (VM A1 em Vinhedo; plano feito, criação perto do M3), V-02 (origem 1 feita; origem 2 perto do M3), V-04 (concluída), V-08 (concluída)

## Contexto

O M1 (coletor local) não consegue começar sem saber **de onde** a coleta vai rodar, porque o lugar muda o que o monitor mede:

- **Latência.** Pela IN 615, 5.3, o consumidor mede o tempo incluindo a rede. Quanto mais longe a origem, mais o p95 do monitor reflete a rede, e não a API. — **Fato** (norma)
- **Bloqueio de origem.** Da origem 1 (IP residencial, Brasil), as 53 URLs de `/personal-loans` responderam com sucesso. — **Evidência** (V-02, rodada 2). Já a possibilidade de alguma instituição bloquear IP de nuvem ou estrangeiro ainda **não foi testada**. — **Hipótese** (V-02, perguntas 1 e 2, pendentes das origens 2 e 3)
- **Regra do coletor.** Os termos do GitHub proíbem usar os runners hospedados como infraestrutura de aplicação, então o GitHub Actions não pode ser o coletor. — **Fato** (texto) / **Inferência** (aplicação; V-08)

Sem essa decisão, o M1 não sabe que origem registrar em cada medição, o M3 não sabe onde criar a VM e o M0 não fecha (CLAUDE.md, seção 10: "ADR-001 aceito").

## Decisão

1. **Toda medição publicada é feita de uma origem no Brasil**, e cada medição registra a sua origem.
   - M1 e M2: computador da pessoa desenvolvedora (origem 1, residencial).
   - A partir do M3: VM Oracle Always Free Ampere A1 na região `sa-vinhedo-1` (origem 2, nuvem), conforme o plano da V-01.
2. **Caminho A → B:**
   - **Etapa A:** a VM coleta e grava Parquet diário, que é o contrato entre coleta e análise.
   - **Etapa B:** começa depois de cerca de 2 semanas de etapa A estável (M8). Os mesmos Parquet são carregados em lote no BigQuery, sem refazer a coleta.
3. **GitHub Actions nunca coleta**; serve só para CI e publicação.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Não decidir agora | O M1 começa sem campo de origem e sem saber onde vai rodar. O M0 não fecha sem o ADR-001 aceito (CLAUDE.md, seção 10). |
| Medir de fora do Brasil (região Oracle ou outra nuvem no exterior) | A rede internacional entra no tempo medido (IN 615, 5.3) e aumenta o viés de latência. Ainda há o risco não testado de bloqueio por país (V-02, pergunta 1). |
| Só a máquina residencial, sem VM | Não garante coleta 24/7 por 4 semanas (Inferência), e operação contínua é parte do que o projeto quer provar (`docs/origem.md`, seção 1, Opinião registrada na decisão). Continua sendo a referência das rodadas da V-02. |
| GitHub Actions como coletor | Proibido pelos termos (V-08). |
| Ir direto à etapa B | O BigQuery entra para fechar o gap de cloud fora da Microsoft, não pela escala (CLAUDE.md, seção 9). Começar por ele exige faturamento ativo antes de existir dado para carregar. O sandbox sem cartão expira em 60 dias, menos que a janela de 90 (`docs/origem.md`, seção 4). |
| São Paulo em vez de Vinhedo | Decidido na V-01 (itens 5 a 7): a latência não desempata as duas regiões. A escolha de Vinhedo é Opinião, apoiada em evidência fraca de menos disputa por A1. |

## Consequências

- **Positivas:**
  - O p95 medido fica mais perto do que um cliente no Brasil vê, o que é a principal correção do viés de latência (`docs/origem.md`, seção 5).
  - Com a origem registrada em cada medição, dá para separar "bloqueio" de "indisponibilidade" quando a origem 2 entrar.
  - O Parquet como contrato permite a etapa B sem refazer a coleta.
- **Negativas (obrigatório):**
  - **A região de origem da Oracle é irreversível** e o Always Free só existe nela (V-01, Fato). Se Vinhedo der problema, não há troca para São Paulo na mesma conta.
  - **A VM pode demorar.** Com 1 AD no Brasil, "out of host capacity" só se resolve esperando. O M3 pode atrasar até 14 dias antes do plano B (V-01, itens 10 e 11).
  - **O coletor 24/7 roda de IP de nuvem**, e o bloqueio a esse tipo de IP é uma Hipótese ainda aberta. Se ele existir, o monitor marcaria como indisponível uma API que está no ar para clientes comuns (V-02, "Por que importa").
  - **As origens 1 e 2 não são comparáveis em latência.** O M1 e o M2 (residencial) e o M3 em diante (nuvem) medem redes diferentes, e as séries precisam ser separadas pela origem, nunca emendadas.
  - **A etapa A não fecha o gap G5** (cloud fora da Microsoft). Ele só fecha na etapa B (`docs/origem.md`, seção 4).
  - Cartão de crédito exigido na Oracle (V-01) e, na etapa B, no Google (V-04).
- **O que muda no projeto:**
  - **M1:** cada medição grava a origem (já previsto no "pronto" do M1). O coletor confia na raiz ICP-Brasil v10 além do `certifi` (V-02, "Efeito no projeto").
  - **M3:** a rodada da origem 2 da V-02 acontece logo depois de criar a VM e **antes** de publicar qualquer número medido dela.
  - **M8/M9:** o gatilho da etapa B é a etapa A estável por cerca de 2 semanas. Cota diária e alerta de orçamento vêm antes da primeira carga (V-04).

## Gatilho de revisão

- **V-02, origem 2:** se uma instituição falhar da VM e responder da origem 1, e isso se repetir em outro dia, abre-se um novo ADR sobre como medir essa instituição (ou declará-la fora da medição de nuvem).
- **V-01:** 14 dias de tentativas sem A1 acionam o ADR do plano B (AMD E2.1.Micro + Prefect Cloud Hobby). A origem continua no Brasil, mas o orquestrador e os marcos mudam.
- **V-08:** se a reconferência antes do M7 mostrar mudança nos termos do GitHub.
- **Etapa A instável:** se não houver 2 semanas estáveis até o M8, o início da etapa B é revisto.

## Fontes

| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| O consumidor mede o tempo incluindo a rede | IN BCB 615/2025, 5.3 e 5.3.2, V, via `docs/origem.md`, seção 5 | 2026-10-08 (laboratório) | Fato |
| Origem 1 (residencial, Brasil): 53/53 com sucesso | `docs/validacoes/V-02_bloqueio-ip-estrangeiro.md`, "Resultado"; `evidencias/V-02/2026-10-18T1745Z_origem1.jsonl` | 2026-10-18 | Evidência |
| Bloqueio de IP de nuvem ou estrangeiro | V-02, "O que já se sabe" e "Pergunta" | 2026-10-18 | Hipótese |
| Região de origem irreversível; Always Free só nela | V-01, "Por que importa" e passo 1 (docs.oracle.com, Always Free Resources) | 2026-10-16 | Fato |
| 1 AD por região no Brasil; espera em "out of host capacity" | V-01, passo 1 (docs.oracle.com, Regions and Availability Domains) | 2026-10-16 | Fato / Inferência |
| Latência não desempata São Paulo e Vinhedo; escolha de Vinhedo | V-01, "Resultado", itens 5 a 7 | 2026-10-18 | Inferência / Opinião |
| Plano B após 14 dias; atraso possível do M3 | V-01, "Resultado", itens 10 e 11 | 2026-10-18 | Inferência |
| GitHub Actions não pode ser coletor | V-08 (GitHub Terms for Additional Products and Features) | 2026-10-08 | Fato / Inferência |
| Carga em lote no BigQuery sem custo | V-04, "Resultado" | 2026-10-18 | Fato |
| Sandbox do BigQuery: 60 dias × janela de 90 | `docs/origem.md`, seção 4 (decisão do laboratório) | 2026-10-08 (laboratório) | Fato |
| BigQuery pelo gap G5, não pela escala; G5 só fecha na etapa B | CLAUDE.md, seção 9; `docs/origem.md`, seção 4 | 2026-10-08 (laboratório) | Evidência / Inferência |
| Raiz ICP-Brasil v10 necessária no coletor | V-02, "Efeito no projeto" | 2026-10-18 | Fato / Evidência |
