# Normas — origem, versões e integridade

Cópias dos textos normativos usados pelo projeto. A fonte de verdade é sempre o BCB; estas cópias existem para auditoria (o que foi lido, quando, com que conteúdo).

## Arquivos

| Arquivo | Norma | Publicação | SHA-256 |
|---|---|---|---|
| `in615.txt` | IN BCB 615, de 6/5/2025 — Manual de APIs do Open Finance, versão 7.0 | DOU de 12/5/2025, Seção 1, p. 217-220 | `a7cbae71c365842007b1e42582e046d150643e598d361354a93c318b55228950` |
| `in706.txt` | IN BCB 706, de 29/1/2026 — Manual de Monitoramento do Open Finance, versão 3.0 | DOU de 2/2/2026, Seção 1, p. 189-192 | `dec0ce25dc7d4800a39dead61cce5f9e99e3c6754f81ca2d500cae87f15897d7` |
| `res32.txt` | Res. BCB 32, de 29/10/2020 — requisitos técnicos do Open Finance | DOU de 3/11/2020, Seção 1, p. 445/446 | `fa7d9b875ec9ceec7c5defbb4a052d914ddaf992f263a0204b53d398db1fe4c6` |
| `brutos/in615.json` | resposta bruta da API (IN 615) | — | `88a38bb8f187767c8b1f763643ee08046b050effe9a21c7897e88b74d3368ee7` |
| `brutos/in706.json` | resposta bruta da API (IN 706) | — | `5d594c91fa3d95dcfaa9c2ac1961bfde5ac4bfa141626087520f8d4c1693b616` |
| `brutos/res32.json` | resposta bruta da API (Res. 32) | — | `62146b6fee1a039b0e174c9aee64e02cd8a850360ea6f57288afec40ac339d42` |
| `brutos/busca_manualapis.json` | busca "Manual de APIs" de 2026-10-08 (laboratório) | — | `942579d2cdf4b8644f4c2eb5d4ddd48be5096d5a879404963141c5e20a0292eb` |
| `brutos/busca_2026-10-10_manual-apis.json` | busca de vigência de 2026-10-10 | — | `b2abd20b3f065ac6bb3e1bc6dc7b70014fc734849f3f7963cc6f120b5d4b5206` |
| `brutos/busca_2026-10-10_manual-monitoramento.json` | busca de vigência de 2026-10-10 | — | `824b312b7a2f4aff65704a7b128d64056b8be79924503c4d8e7c2c6ed7eea863` |

- Os `.txt` são o campo `Texto` dos `.json`, sem HTML e com espaços normalizados (feitos no laboratório).
- Hashes calculados em 2026-10-10 com `sha256sum`. Para conferir: `sha256sum docs/normas/*.txt docs/normas/brutos/*.json`.

## Origem

- **Obtidos em 2026-10-08** no laboratório de pesquisa que escolheu o projeto (`06_oportunidades/auditoria/`), uma requisição por norma, e copiados sem alteração em 2026-10-10 (cópia conferida byte a byte).
- **API de texto integral do BCB** (formato conferido em 2026-10-10):
  - `https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Instrução Normativa BCB&p2=615`
  - `https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Instrução Normativa BCB&p2=706`
  - `https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Resolução BCB&p2=32`
- **Página pública:** `https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Instrução Normativa BCB&numero=615` (respondeu HTTP 200 em 2026-10-10; trocar `tipo` e `numero` para as outras).

## Vigência — histórico de conferências

| Data | Como | Resultado | Rótulo |
|---|---|---|---|
| 2026-10-08 | Busca "Manual de APIs" (laboratório, `brutos/busca_manualapis.json`) | IN 615 é a versão mais recente do Manual de APIs (7.0) | Evidência |
| 2026-10-10 | Busca de normativos do BCB, ordenada por data, termos "Manual de APIs do Open Finance" e "Manual de Monitoramento do Open Finance" (`brutos/busca_2026-10-10_*.json`) | IN 615 (Manual de APIs 7.0) e IN 706 (Manual de Monitoramento 3.0) com `Revogado=0`; nenhuma versão posterior dos dois manuais nos resultados. As versões anteriores aparecem com `Revogado=1` (ex.: IN 575, Monitoramento 2.0) | Evidência |
| 2026-10-10 | Texto integral baixado de novo pela API e comparado com as cópias | Campo `Texto` **idêntico** nas três normas | Fato |

Procedimento da busca (para repetir):
`https://www.bcb.gov.br/api/search/app/normativos/buscanormativos?querytext=ContentType:normativo AND contentSource:normativos AND <termos>&rowlimit=15&startrow=0&sortlist=Data1OWSDATE:descending&refinementfilters=`

Observação: a mesma busca mostra manuais mais novos de **outros** temas — Segurança 5.0 (IN 720, 2026-04-02), Escopo de Dados e Serviços 8.0 (IN 759, 2026-07-09), Experiência do Cliente 9.0 (IN 760). O de Escopo pode definir quais APIs de Dados Abertos são obrigatórias (**Hipótese**; ver V-07). Nenhum deles foi baixado ainda.

## Uso público destas cópias

A Lei 9.610/1998, art. 8º, IV, exclui da proteção de direito autoral "os textos de tratados ou convenções, leis, decretos, regulamentos, decisões judiciais e demais atos oficiais" (**Inferência** de que cobre instruções normativas do BCB; conferir o texto da lei no Planalto antes da v1.0). `[VALIDAR]`
