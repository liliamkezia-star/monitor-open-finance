# Permissões do Claude Code neste projeto

JSON não aceita comentários; o motivo de cada regra fica aqui. Sintaxe conferida em https://code.claude.com/docs/en/permissions (lida em 2026-10-10). Ordem de avaliação: **deny → ask → allow**; uma regra `allow` não abre exceção em uma `deny`.

## `.claude/settings.json` (versionado)

| Regra | Tipo | Motivo |
|---|---|---|
| `WebSearch` | allow | Localizar a fonte oficial antes de afirmar algo (CLAUDE.md, seção 6) |
| `WebFetch(domain:www.bcb.gov.br)` | allow | Normas e busca de normativos do BCB (vigência da IN 615 e da IN 706) |
| `WebFetch(domain:github.com)`, `api.github.com`, `raw.githubusercontent.com` | allow | Especificações oficiais em `OpenBanking-Brasil/openapi`, fixadas por SHA |
| `WebFetch(domain:docs.github.com)` | allow | Termos e limites do GitHub Actions (V-08) |
| `WebFetch(domain:openfinancebrasil.org.br)` e `*.openfinancebrasil.org.br` | allow | Portal do Open Finance: termos de uso, limites por origem, classe de frequência (V-03, V-06) |
| `WebFetch(domain:docs.oracle.com)`, `www.oracle.com` | allow | Always Free, regiões e FAQ da Oracle (V-01) |
| `WebFetch(domain:cloud.google.com)`, `docs.cloud.google.com` | allow | Free tier e preços do BigQuery (V-04) |
| `Bash`/`PowerShell`: `git status`, `git diff *`, `git log *` | allow | Leitura do estado do repositório para a revisão de código. `commit` e `push` continuam pedindo permissão |
| `Read(//**/.env)`, `Read(//**/.env.*)` | deny | Política de segredos (CLAUDE.md, seção 11). Arquivos `.env` em qualquer pasta, qualquer que seja a pasta em que a sessão começou |
| `Read(//**/*.pem)`, `*.key`, `*.p12`, `*.pfx` | deny | Chaves privadas e certificados, em qualquer pasta |
| `Read(~/.ssh/**)`, `~/.oci/**`, `~/.config/gcloud/**` | deny | Chaves SSH (M3), credenciais da Oracle (M3) e do Google Cloud (M9) |
| `Edit(...)` com os mesmos padrões | deny | Uma `deny` de `Read` já bloqueia `Edit` e `Write` no mesmo caminho; a `deny` de `Edit` cobre também o NotebookEdit e deixa a intenção explícita |

### Por que `//**/` e não `.env` ou `**/.env`

Conferido na documentação (seção "Read and Edit", lida em 2026-10-10):
- Padrões sem barra seguem a sintaxe do gitignore e **casam em qualquer subpasta**: `Read(.env)` e `Read(**/.env)` são equivalentes.
- Mas padrões relativos ancoram na **pasta em que a sessão começou**: eles bloqueiam o `.env` "at or under the current directory", e não o de uma pasta acima. Uma sessão aberta em `docs/` deixaria o `.env` da raiz desprotegido.
- `//**/.env` ancora na raiz do sistema de arquivos e casa em qualquer lugar ("any `.env` anywhere on the filesystem"). Não depende de onde a sessão começa e não expõe nenhum caminho pessoal.
- No Windows, os caminhos são convertidos para a forma POSIX antes da comparação; `//**/` cobre todos os drives.

### `.env.example` fica bloqueado

- A documentação aceita `!` como exceção em listas `deny` (negação do gitignore), por exemplo `Read(*.env)` seguido de `Read(!sample.env)`.
- Mas há limites documentados: um padrão `!` é lido relativo à pasta atual e **não alcança regras ancoradas com `//`, `~/` ou `/`**; a exceção também vale só para regras do mesmo arquivo de configuração.
- Como as regras agora usam `//**/`, a exceção `Read(!.env.example)` não teria efeito e foi removida.
- **Consequência aceita:** o Claude não lê nem edita o `.env.example`. Não há problema, porque ele não tem valores; quem o mantém é a pessoa desenvolvedora.

Fica **sem** regra `allow`, de propósito:
- **ArtifactData** (rastreador de estudo): a ferramenta não separa leitura de escrita. O pedido de permissão a cada uso é a trava contra escrever no rastreador.
- **Edit/Write** em geral: cada mudança de arquivo pede ok (CLAUDE.md, seção 6).
- **WebFetch** para APIs das instituições: chamadas às APIs medidas são feitas pelo código do projeto, nunca pelo Claude.

## Regras futuras

- Quando uma pasta de código nascer (ex.: `src/`, `tests/`, `dbt/`), adicionar `deny` de `Edit` para ela, por exemplo `Edit(src/**)`. Isso faz valer a regra "todo o código é escrito pela pessoa desenvolvedora".

## `.claude/settings.local.json` (fora do git)

| Regra | Tipo | Motivo |
|---|---|---|
| `Read(//<caminho do laboratório>/**)` | allow | Consultar o laboratório de origem sem pedir permissão a cada leitura |
| `Edit(//<caminho do laboratório>/**)` | deny | O laboratório é só leitura |

No Windows, os caminhos são convertidos para a forma POSIX antes da comparação (`C:\Users\...` vira `/c/Users/...`); o prefixo `//` indica caminho absoluto.

## Limite conhecido

As regras `deny` valem para as ferramentas do Claude e para comandos de arquivo reconhecidos no shell (`cat`, `head` etc.). **Não** valem para um script (Python, por exemplo) que abra arquivos sozinho. Por isso o `.gitignore` e a varredura de segredos no CI (M7) continuam obrigatórios.
