# V-01 — VM Ampere A1 Always Free em São Paulo ou Vinhedo

- **Status:** Em andamento — passos 1 a 3 feitos (plano definido em 2026-10-18); **criação da VM adiada para perto do M3** (ver "Plano")
- **Prioridade:** Alta — primeira tarefa do M0, semana de 2026-10-12
- **Etapa / marco afetado:** A; M3 (servidor), M4 (orquestrador)
- **Origem da pendência:** laboratório, `07_projeto_final/2026-10-08_decisao.md`, seção 4, "Riscos que ficam abertos"; anexo de custo zero, seção 2

## Pergunta

É possível criar uma VM Ampere A1 Always Free (2 OCPUs / 12 GB) com região de origem `sa-saopaulo-1` (São Paulo) ou `sa-vinhedo-1` (Vinhedo)?

## Por que importa

- Medir do Brasil é a principal correção do viés de latência (anexo, seção 5).
- **A região de origem não pode ser trocada depois** e as instâncias Always Free só podem ser criadas nela ("You must create the Always Free compute instances in your home region", Oracle, lido em 2026-10-08 — Fato).
- O Airflow é escolha **condicionada** a esta validação (CLAUDE.md, seção 9). Se falhar, o plano B da decisão é usar as VMs AMD E2.1.Micro com Prefect Cloud Hobby, e isso exige um ADR e a revisão de marcos e tópicos.

## O que já se sabe (laboratório, 2026-10-08)

- Regiões no Brasil: `sa-saopaulo-1` (GRU) e `sa-vinhedo-1` (VCP). Fato (docs.oracle.com, regiões).
- Free Tier "available in all regions where commercial Oracle Cloud Infrastructure service is available". Fato (FAQ).
- A tabela oficial de disponibilidade por região deu HTTP 403. Relatos de usuários apontam falta de A1 em São Paulo. Evidência fraca, não verificada.
- "Out of host capacity" pode atrasar a criação por dias. Fato (FAQ).
- Cartão de crédito exigido (não aceita pré-pago nem virtual). Fato (FAQ).

## Como verificar

**Passo a passo guiado, feito junto, antes de criar a conta.** Rascunho dos tópicos da conversa:
1. Reler as páginas oficiais (Always Free, regiões, FAQ) e anotar a data de acesso.
2. Discutir os critérios de escolha entre São Paulo e Vinhedo (ex.: disponibilidade de A1, proximidade de rede com as instituições, o que fazer se a A1 não aparecer). Cada critério precisa de fonte ou fica rotulado como Opinião/Hipótese.
3. Combinar o plano para "out of host capacity" (quantas tentativas, por quantos dias, quando acionar o plano B).
4. Só então criar a conta, escolher a região e tentar criar a instância.
5. Registrar o resultado aqui, **sem** dados pessoais, de cartão, e-mail ou OCID.

Não fazer: criar a conta antes do passo 2; guardar capturas com dados da conta.

## Execução

### Passo 1 — Releitura das páginas oficiais

- **Data:** 2026-10-16
- **Quem:** mentoria (leitura); redação em 2026-10-18; revisão pela pessoa desenvolvedora em 2026-10-18
- **Fonte(s):** acesso em 2026-10-16 (links reconferidos com HTTP 200 em 2026-10-18)
  - "Always Free Resources": https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
  - "Regions and Availability Domains": https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
  - FAQ do Free Tier (`oracle.com/cloud/free/faq`): HTTP 403 de novo, **não reconferido**
- **O que foi feito:** leitura das duas páginas da documentação. Nada da conta foi criado.

| Item | O que a página diz | Rótulo |
|---|---|---|
| Cota A1 | 1.500 OCPU-hora + 9.000 GB-hora por mês, o que dá cerca de 2 OCPUs e 12 GB ligados o mês todo | Fato |
| Região | Instâncias Always Free só na região de origem | Fato |
| "Out of host capacity" | A orientação é tentar outro domínio de disponibilidade (AD) ou esperar | Fato |
| ADs no Brasil | `sa-saopaulo-1` (GRU) e `sa-vinhedo-1` (VCP) têm **1 AD cada** | Fato |
| Consequência | No Brasil, "tentar outro AD" é impossível; só resta esperar e tentar de novo | Inferência |
| Recuperação por ociosidade | Instância Always Free pode ser recuperada se, em 7 dias, o p95 de CPU, rede **e** memória ficarem todos abaixo de 20% (a regra de memória vale só para A1) | Fato |
| Armazenamento e tráfego | 200 GB de block volume no total; 10 TB por mês de saída | Fato |

### Passos 2 e 3 — Critérios e plano (conversa guiada)

- **Data:** 2026-10-18
- **Quem:** pessoa desenvolvedora (respostas e decisões); mentoria (perguntas e redação); revisão pela pessoa desenvolvedora em 2026-10-18
- **O que foi feito:** cinco perguntas, respondidas pela pessoa desenvolvedora. As decisões estão em "Resultado".

## Resultado

### Ociosidade

1. **A memória é a métrica que mantém a VM ativa.** A regra exige as três métricas abaixo de 20% ao mesmo tempo, então basta uma acima. CPU e rede de um monitor leve (poucos KB por chamada, a maior parte do tempo em espera) ficam com p95 perto de zero. Já a memória ocupada por serviços residentes fica alocada 24 horas por dia. — **Fato** (regra) / **Inferência** (comportamento do monitor)
2. Airflow + banco ocupam mais de 2,4 GB (20% de 12 GB). — **Hipótese.** Como testar: medir o p95 de memória da VM durante 7 dias no M3/M4.
3. **Uma VM parada é recuperável.** Se a VM for criada muito antes de ter uso, ela pode ser recuperada em 7 dias. — **Inferência** (aplicação da regra)
4. **O plano B tem o mesmo risco, maior.** Uma VM AMD E2.1.Micro (1 GB) com Prefect leve pode ficar abaixo de 20% nas três métricas. Isso precisa entrar no ADR do plano B, se ele for acionado. — **Hipótese**

### Região

5. **A latência não decide entre as duas regiões.** São cerca de 80 km de distância, o que dá cerca de 1 a 2 ms por ida e volta e poucos ms no total de uma requisição. Além disso, geografia não é topologia de rede. — **Inferência.** Não é Hipótese porque não dá para testar no projeto: com a região de origem irreversível e o Always Free só nela, nunca haverá duas VMs para comparar.
6. Nenhum critério verificável desempata as duas regiões **antes** da escolha. Capacidade e reputação do IP só são observáveis depois de escolher, e a trava da região de origem é uma restrição igual para as duas. — **Inferência**
7. **Escolha: `sa-vinhedo-1` (Vinhedo).** Justificativa da pessoa desenvolvedora: menos disputa por capacidade A1 do que em São Paulo. — **Opinião**, apoiada em evidência fraca: relatos de usuários de falta de A1 em São Paulo, sem amostra nem verificação (ver "O que já se sabe").

### Plano

8. **Quando:** as tentativas de criar a VM começam **perto da rodada da V-02 na nuvem, e essa rodada fica para perto do início do M3** (decisão "a"). Assim a VM entra em uso logo depois de criada e não fica parada até ser recuperada. A **conta** pode ser criada antes, porque a escolha da região acontece nela.
9. **Como:** 1 a 2 tentativas **manuais** por dia, pelo painel. **Sem script de insistência** (nada de tentativas a cada poucos minutos pela OCI CLI): seria um comportamento abusivo, com risco de bloqueio, e incoerente com a regra "não retentar em rajada" da V-02.
10. **Gatilho do plano B:** **14 dias** de tentativas sem conseguir a instância A1. Aí abre-se o ADR do substituto (plano da decisão: VMs AMD E2.1.Micro com Prefect Cloud Hobby) e a revisão de marcos e tópicos (CLAUDE.md, seção 9).
11. **Custo do plano:** se a capacidade demorar, o M3 pode atrasar até 14 dias. Para reduzir esse atraso, as tentativas podem começar um pouco antes da data prevista do M3, aceitando um intervalo curto de VM parada (menos de 7 dias). — **Inferência**

## Efeito no projeto

- **M0:** a V-01 fecha o M0 com **plano e bloqueio declarados** ("execução adiada para perto do M3"), como o "pronto" do M0 permite ("resultado ou bloqueio declarado").
- **V-02:** a rodada da origem 2 (VM na nuvem) acontece perto do M3, junto com as tentativas desta validação.
- **M3/M4:** medir o p95 de memória nos 7 primeiros dias da VM (item 2).
- **Passo 4** (criar a conta e escolher Vinhedo) pode ser feito quando a pessoa desenvolvedora quiser. O resultado das tentativas entra aqui como "Execução — passo 4", **sem** dados pessoais, de cartão, e-mail ou OCID.
- Reconferir a página "Always Free Resources" (cotas e regra de ociosidade) antes da primeira tentativa.
