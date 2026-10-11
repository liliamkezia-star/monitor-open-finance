# Progresso

## Situação atual

- **Marco:** M0 — Fundação
- **Início do projeto:** 2026-10-12 (decisão da fase 07)
- **Estudo:** 2026-10-12 a 2026-12-13 (rastreador; endereço em `CLAUDE.local.md`)
- **Última leitura do rastreador:** 2026-10-10 — tópico 1 "estudando"; tópicos 2 a 13 "não iniciado"; nenhum "dominado".

## M0 — checklist do "pronto"

- [x] Estrutura inicial, `CLAUDE.md`, skills, `settings.json` e `PERMISSOES.md` (2026-10-10)
- [x] `docs/normas/`: textos, brutos, hashes, LEIAME com vigência reconfirmada em 2026-10-10
- [x] `docs/normas/sla.md` com todos os números citados e trechos conferidos (2026-10-10)
- [x] `docs/especificacoes/VERSOES.md`: commit fixado e hashes das 3 famílias do MVP (2026-10-10)
- [x] `docs/origem.md`
- [ ] **V-01** — A1 em São Paulo ou Vinhedo · **prioritária, semana de 12/10** · passo a passo guiado **antes** de criar a conta
- [ ] **V-03** — termos do Portal e do Diretório; limites por origem · **prioritária, semana de 12/10**
- [ ] V-02 — bloqueio de IP estrangeiro (desenho no M0; execução depende da VM e do tópico 1)
- [ ] V-04 — carga em lote no BigQuery (pode ficar "bloqueada até a etapa B", com justificativa)
- [ ] V-05 — licença das especificações
- [ ] V-06 — classe de frequência dos endpoints
- [ ] V-07 — Manual de Escopo de Dados 8.0
- [x] V-08 — termos do GitHub Actions (herdada; reconferir antes do M7)
- [ ] ADR-001 escrito pela pessoa desenvolvedora (mentoria pela skill `adr`) e aceito
- [ ] Revisão de todos os arquivos do M0 pela pessoa desenvolvedora
- [ ] `git init` e primeiro commit, sem segredos, feitos pela pessoa desenvolvedora

## Dependências de estudo por marco

| Marco | Tópicos | Situação em 2026-10-10 |
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

## Bloqueios e riscos ativos

- V-01: a região de origem da Oracle é irreversível; "out of host capacity" pode atrasar dias.
- Janela de 90 dias: com a coleta 24/7 prevista para meados de novembro, a janela só completa em meados de fevereiro; a v1.0 declara a janela parcial.

## Diário

Entradas curtas, mais recente no topo: data · o que foi feito · o que ficou · próximo passo · tópicos usados.

### 2026-10-10
- **Feito:** base do M0 criada com a mentoria (estrutura, CLAUDE.md, skills, permissões, normas, SLA, especificações, modelos de validação e ADR, origem). Vigência da IN 615 e da IN 706 reconfirmada; textos idênticos aos guardados.
- **Ficou:** V-01 a V-07; ADR-001; revisão e primeiro commit.
- **Próximo passo:** semana de 12/10 — V-01 (guiada) e V-03.
- **Tópicos usados:** nenhum.
