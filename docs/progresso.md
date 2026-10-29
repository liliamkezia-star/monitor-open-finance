# Progresso

## Situação atual

- **Marco:** M1 — Coletor local (M0 concluído em 2026-10-29, PR #7)
- **Início do projeto:** 2026-10-12 (decisão da fase 07)
- **Estudo:** 2026-10-12 a 2026-12-13 (rastreador; endereço em `CLAUDE.local.md`)
- **Última leitura do rastreador:** 2026-10-29 — tópicos 1 a 4 **dominados** (liberados em 17/10, 18/10, 22/10 e 24/10); tópicos 5 a 13 "não iniciado".

## M0 — checklist do "pronto"

- [x] Estrutura inicial, `CLAUDE.md`, skills, `settings.json` e `PERMISSOES.md` (2026-10-10)
- [x] `docs/normas/`: textos, brutos, hashes, LEIAME com vigência reconfirmada em 2026-10-10
- [x] `docs/normas/sla.md` com todos os números citados e trechos conferidos (2026-10-10)
- [x] `docs/especificacoes/VERSOES.md`: commit fixado e hashes das 3 famílias do MVP (2026-10-10)
- [x] `docs/origem.md`
- [x] **V-01** — plano definido (2026-10-18): Vinhedo; tentativas manuais perto do M3; plano B depois de 14 dias · execução **adiada para perto do M3** (bloqueio declarado)
- [x] **V-03** — termos do Portal e do Diretório; limites por origem (2026-10-16; 3 itens `[VALIDAR]` registrados)
- [x] **V-02** — bloqueio de IP estrangeiro ou de nuvem · origem 1 feita em 2026-10-18 (53/53, com a raiz ICP-Brasil) · origem 2 **adiada para perto do M3**, depende da VM da V-01 (bloqueio declarado); origem 3 opcional
- [x] V-04 — carga em lote no BigQuery (2026-10-18: gratuita pelo pool compartilhado; custo só acima de 10 GiB de armazenamento ou 1 TiB de consultas por mês; reconferir antes do M9)
- [x] V-05 — licença das especificações (2026-10-18: sem licença declarada; YAMLs continuam fora do git)
- [x] V-06 — classe de frequência dos endpoints (2026-10-16, junto com a V-03: as 6 rotas do MVP são "Baixa")
- [x] V-07 — Manual de Escopo de Dados 8.0 (2026-10-18: vigente a partir de 3/11/2026; define os dados obrigatórios, não as instituições; 1 `[VALIDAR]`)
- [x] V-08 — termos do GitHub Actions (herdada; reconferir antes do M7)
- [x] ADR-001 escrito pela pessoa desenvolvedora (mentoria pela skill `adr`) e aceito
- [x] Revisão de todos os arquivos do M0 pela pessoa desenvolvedora (2026-10-29)
- [x] `git init` e primeiro commit, sem segredos, feitos pela pessoa desenvolvedora (`52976fa`, 2026-10-10)

## Dependências de estudo por marco

| Marco | Tópicos | Situação em 2026-10-29 |
|---|---|---|
| M0 | — | concluído |
| M1 | 1, 2, 3 | liberado (1, 2 e 3 dominados) |
| M2 | 6 | bloqueado |
| M3 | 4, 5 | bloqueado (4 dominado; 5 não iniciado) |
| M4 | 7 | bloqueado (e condicionado à V-01) |
| M5 | 8, 9 | bloqueado |
| M6 | 10 | bloqueado |
| M7 | 11 | bloqueado |
| M9 | 12 | bloqueado |
| M10 | 13 | bloqueado |

## Entradas para o ADR de frequência do M1

Saídas da V-03 e da V-06, para não se perderem até o M1 (decisão final no ADR):

- **APIs das instituições:** 1 requisição a cada 15 min por endpoint, mantida. A margem é de mais de 7.500 vezes sobre qualquer limite publicado (V-03, pergunta 2).
- **Diretório:** consultar 1 vez por dia, de preferência com requisição condicional pelo `ETag`, e manter a última lista válida se ele falhar. O guia do Diretório recomenda "revalidação diária" (V-03, Diretório).
- **Timeout:** a tabela oficial dá 15 s para as rotas do MVP. É uma referência para o timeout do coletor.
- **HTTP 429:** registrar e nunca retentar em rajada.
- **p95 de referência no M5:** 4.000 ms para as 6 rotas (classe Baixa; IN 615, 5.3.2, III).

## Bloqueios e riscos ativos

- V-01: região de origem irreversível (escolha: Vinhedo). "Out of host capacity" pode atrasar o M3 em até 14 dias (gatilho do plano B). VM parada por 7 dias pode ser recuperada pela Oracle; por isso a VM só é criada perto do M3.
- V-02: bloqueio de IP de **nuvem** (não só estrangeiro) é uma Hipótese nova; se confirmada, afeta o coletor 24/7.
- Janela de 90 dias: com a coleta 24/7 prevista para meados de novembro, a janela só completa em meados de fevereiro; a v1.0 declara a janela parcial.
- Fontes oficiais que mudam (termos do Portal, página Referência da wiki): reconferir versão e data antes de publicar resultados.

## Diário

Entradas curtas, mais recente no topo: data · o que foi feito · o que ficou · próximo passo · tópicos usados.

### 2026-10-29
- **Feito (fim do dia):** revisão do M0 concluída pela pessoa desenvolvedora (hashes, trechos e links conferidos); errata do ADR-001 (5.3 → 5.3.2, V); PR #7 mergeado. **M0 concluído.** Rastreador relido: tópicos 1 a 4 dominados, M1 liberado. README com status M1.
- **Próximo passo:** M1 — ADR de frequência (entradas acima) e escolha do modo de código do coletor.
- **Feito:** ADR-001 aceito (PR #6): medir do Brasil, com a origem registrada em cada medição; caminho A → B pelo Parquet diário; GitHub Actions nunca coleta. Pendências da V-01 e da V-02 (origem 2) viraram gatilhos de revisão. Conferência do "pronto" do M0. `.gitattributes` com `*.jsonl text eol=lf`: com `core.autocrlf=true`, a cópia local das evidências da V-02 ganhava CRLF e o SHA-256 deixava de bater com o registrado (o conteúdo no git estava certo).
- **Ficou:** revisão de todos os arquivos do M0 pela pessoa desenvolvedora; reler o rastreador antes de declarar o M1; `[VALIDAR]` da V-03, da V-07, da V-04 (M9) e do `VERSOES.md` (M6).
- **Próximo passo:** revisão final do M0; depois, marco M1 e status do README.
- **Tópicos usados:** nenhum (só documentação).

### 2026-10-18
- **Correção (2026-10-29):** o script local da V-02 e a V-04 foram feitos no mesmo dia, à tarde (PRs #4 e #5). O script foi escrito pelo Claude e revisado pela pessoa desenvolvedora (V-02, "Execução").
- **Feito:** rastreador relido (tópico 1 dominado). V-01, passos 2 e 3: Vinhedo (Opinião), tentativas manuais perto do M3 para evitar a recuperação por ociosidade, plano B depois de 14 dias. V-02 ampliada para 3 origens (residencial, nuvem no Brasil, exterior). V-05 concluída (sem licença declarada). V-07 concluída (IN 759 guardada em `docs/normas/`; vigente a partir de 3/11/2026; define os dados obrigatórios, não as instituições). Rascunhos da mentoria revisados pela pessoa desenvolvedora.
- **Ficou:** V-02 (script local da origem 1), V-04; ADR-001; revisão dos arquivos do M0; `[VALIDAR]` da V-03 e da V-07 (Resolução Conjunta nº 1/2020); passo 4 da V-01 (criar a conta).
- **Próximo passo:** script local da V-02 (origem 1), escrito pela pessoa desenvolvedora com o tópico 1.
- **Tópicos usados:** 1 (desenho do registro e da regra de não retentar na V-02); nenhum código escrito.

### 2026-10-16
- **Feito:** V-03 concluída: termos do Portal (omissos sobre coleta automatizada; reprodução proibida, daí a regra "dado com fonte, sem cópia da página"); Diretório (sem termos para a lista pública, sem `robots.txt`; guia recomenda revalidação diária); limite por origem aplicável a Dados Abertos e a divergência de TPM (500 na tabela × 1.000 na norma) registradas. V-06 concluída junto (6 rotas "Baixa", p95 de 4.000 ms). Política para `robots.txt` aceita. Rastreador relido.
- **Ficou:** V-01, V-02, V-04, V-05 e V-07; ADR-001; revisão dos arquivos do M0; `[VALIDAR]` da V-03 (Res. BCB 294/2023, versão mais nova do guia do Diretório, marcação "aplicável" por endpoint).
- **Próximo passo:** V-01 (guiada, antes de criar a conta); commit das validações pela pessoa desenvolvedora.
- **Tópicos usados:** nenhum (só leitura de documentos; nenhum código).

### 2026-10-10
- **Feito:** base do M0 criada com a mentoria (estrutura, CLAUDE.md, skills, permissões, normas, SLA, especificações, modelos de validação e ADR, origem). Vigência da IN 615 e da IN 706 reconfirmada; textos idênticos aos guardados.
- **Ficou:** V-01 a V-07; ADR-001; revisão e primeiro commit.
- **Próximo passo:** semana de 12/10 — V-01 (guiada) e V-03.
- **Tópicos usados:** nenhum.
