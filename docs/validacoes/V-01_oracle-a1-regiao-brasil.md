# V-01 — VM Ampere A1 Always Free em São Paulo ou Vinhedo

- **Status:** Pendente
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

- **Data:**
- **Quem:**
- **Fonte(s):**
- **O que foi feito:**

## Resultado

—

## Efeito no projeto

—
