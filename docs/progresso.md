# Progresso

## Situação atual

- **Marco:** M0 — Fundação
- **Início do projeto:** 2026-10-12 (decisão da fase 07)
- **Estudo:** 2026-10-12 a 2026-12-13 (rastreador; endereço em `CLAUDE.local.md`)
- **Última leitura do rastreador:** 2026-10-16 — tópico 1 "estudando" (exercícios 1.1 a 1.4 feitos; faltam os blocos 1.5, repositório e PR, e 1.6, tempo por fase da requisição); tópicos 2 a 13 "não iniciado"; nenhum "dominado".

## M0 — checklist do "pronto"

- [x] Estrutura inicial, `CLAUDE.md`, skills, `settings.json` e `PERMISSOES.md` (2026-10-10)
- [x] `docs/normas/`: textos, brutos, hashes, LEIAME com vigência reconfirmada em 2026-10-10
- [x] `docs/normas/sla.md` com todos os números citados e trechos conferidos (2026-10-10)
- [x] `docs/especificacoes/VERSOES.md`: commit fixado e hashes das 3 famílias do MVP (2026-10-10)
- [x] `docs/origem.md`
- [ ] **V-01** — A1 em São Paulo ou Vinhedo · **prioritária** · passo a passo guiado **antes** de criar a conta
- [x] **V-03** — termos do Portal e do Diretório; limites por origem (2026-10-16; 3 itens `[VALIDAR]` registrados)
- [ ] V-02 — bloqueio de IP estrangeiro (desenho no M0; execução depende da VM e do tópico 1)
- [ ] V-04 — carga em lote no BigQuery (pode ficar "bloqueada até a etapa B", com justificativa)
- [ ] V-05 — licença das especificações
- [x] V-06 — classe de frequência dos endpoints (2026-10-16, junto com a V-03: as 6 rotas do MVP são "Baixa")
- [ ] V-07 — Manual de Escopo de Dados 8.0
- [x] V-08 — termos do GitHub Actions (herdada; reconferir antes do M7)
- [ ] ADR-001 escrito pela pessoa desenvolvedora (mentoria pela skill `adr`) e aceito
- [ ] Revisão de todos os arquivos do M0 pela pessoa desenvolvedora
- [x] `git init` e primeiro commit, sem segredos, feitos pela pessoa desenvolvedora (`52976fa`, 2026-10-10)

## Dependências de estudo por marco

| Marco | Tópicos | Situação em 2026-10-16 |
|---|---|---|
| M0 | — | liberado |
| M1 | 1, 2, 3 | bloqueado (1 estudando; 2 e 3 não iniciados) |
| M2 | 6 | bloqueado |
| M3 | 4, 5 | bloqueado |
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

- V-01: a região de origem da Oracle é irreversível; "out of host capacity" pode atrasar dias.
- Janela de 90 dias: com a coleta 24/7 prevista para meados de novembro, a janela só completa em meados de fevereiro; a v1.0 declara a janela parcial.
- Fontes oficiais que mudam (termos do Portal, página Referência da wiki): reconferir versão e data antes de publicar resultados.

## Diário

Entradas curtas, mais recente no topo: data · o que foi feito · o que ficou · próximo passo · tópicos usados.

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
