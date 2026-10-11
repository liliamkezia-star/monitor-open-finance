# Monitor externo do Manual de APIs do Open Finance Brasil

> **Status: em construção (M0 — Fundação).** Ainda não há coleta nem resultados publicados.

Monitor que mede, de fora e a partir do Brasil, as APIs públicas de **Dados Abertos** do Open Finance Brasil — disponibilidade, tempo de resposta (p95) e conformidade com as especificações oficiais — e compara as medições com os limites do Manual de APIs do Open Finance (IN BCB 615/2025, versão 7.0).

## O que este projeto é — e o que não é

- Os resultados são **estimativas externas**, feitas do ponto de vista de um consumidor, com amostragem (1 requisição a cada 15 minutos por endpoint).
- **Não** é a métrica oficial do SLA, que usa todas as requisições de cada minuto e é apurada pela Estrutura de Governança do Open Finance.
- **Não** afirma que uma instituição violou ou descumpriu o SLA.
- **Não** faz teste de carga e não tenta provocar erros de sobrecarga.
- Fora do escopo: APIs autenticadas e o índice de qualidade de dados da IN BCB 706/2026.

Base normativa, com os trechos citados: [`docs/normas/sla.md`](docs/normas/sla.md).

## Documentação

- [Origem do projeto e arquitetura](docs/origem.md)
- [Progresso](docs/progresso.md)
- [Decisões de arquitetura (ADRs)](docs/adr/README.md)
- [Normas: origem, vigência e integridade](docs/normas/LEIAME.md)
- [Versão fixada das especificações](docs/especificacoes/VERSOES.md)
- [Validações](docs/validacoes/README.md)

## Escolhas de tecnologia

Cada ferramenta entra com um ADR que diz o problema que ela resolve. Em particular: o BigQuery (etapa B) entra para demonstrar uma cloud fora da Microsoft, **não por necessidade de escala** — o volume previsto é de cerca de 1 GB por ano.

## Como este projeto é feito

Todo o código é escrito à mão pela pessoa autora do projeto. Um assistente de IA (Claude Code) atua como mentor técnico: explica, faz perguntas, dá dicas e revisa; as regras desse trabalho estão em [`CLAUDE.md`](CLAUDE.md) e em [`.claude/`](.claude/).

## Licenças

- **Código:** [MIT](LICENSE).
- **Documentação e dados produzidos pelo projeto:** [CC BY 4.0](LICENSE-docs.md).
- Os textos normativos em `docs/normas/` são atos oficiais do Banco Central do Brasil, reproduzidos para auditoria (ver `docs/normas/LEIAME.md`).
- As especificações OpenAPI oficiais **não** são redistribuídas aqui; são baixadas de um commit fixado (ver `docs/especificacoes/VERSOES.md`).
