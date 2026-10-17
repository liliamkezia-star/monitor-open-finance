# V-03 — Termos de uso do Portal e do Diretório; limites por origem

- **Status:** Concluída (2026-10-16)
- **Prioridade:** Alta — tarefa do M0, semana de 2026-10-12
- **Etapa / marco afetado:** A; M1 (ADR de frequência), CLAUDE.md seção 5
- **Origem da pendência:** laboratório, oportunidades, seção 8; decisão, seção 4

## Pergunta

1. O Portal do Open Finance e o Diretório de Participantes têm termos de uso que restrinjam a coleta automatizada, a republicação dos resultados ou a frequência de acesso?
2. Para os endpoints de Dados Abertos das 3 famílias do MVP, o limite por origem está marcado como "aplicável" ou "não aplicável" no Portal, e com que classe de frequência?

## Por que importa

- Define se o projeto pode existir como está e com que frequência (valor inicial: 1 requisição a cada 15 minutos por endpoint).
- A IN 615, 5.1.1, remete ao Portal: "A informação se o limite por origem é "aplicável" ou "não aplicável" deve estar explícito por endpoint no Portal do Open Finance ." (Fato; ver `docs/normas/sla.md`, seção 3)

## Como verificar

- Ler os termos de uso do Portal (`openfinancebrasil.org.br`) e do Diretório (`data.directory.openbankingbrasil.org.br`), guardando URL, data e trecho literal.
- Procurar no Portal a página de classificação de endpoints (frequência e aplicabilidade do limite por origem). Se for a mesma fonte da V-06, registrar a ligação entre as duas.
- Se os termos forem omissos, registrar "omisso" (isso é um resultado), sem inferir permissão.

## Execução

### Parte 1 — Termos do Portal

- **Data:** 2026-10-16
- **Quem:** pessoa desenvolvedora (leitura); mentoria (redação); revisão pela pessoa desenvolvedora em 2026-10-16
- **Fonte(s):** https://openfinancebrasil.org.br/termos-e-condicoes-de-uso/ — "Termos e condições de uso", revisão de 15 de julho de 2021 (data no topo da página, cláusula 4.2); acesso em 2026-10-16
- **O que foi feito:** leitura integral dos termos (preâmbulo e seções 1 a 9) e busca no texto completo pelas palavras "robô", "automatizad", "scraping", "API", "acesso" e "limite". Nenhuma cópia da página foi guardada no repositório (cláusula 7.2.1).

| Palavra | Ocorrências | Onde | Relação com coleta automatizada |
|---|---|---|---|
| robô | 0 | — | — |
| automatizad | 0 | — | — |
| scraping | 0 | — | — |
| API | 1 | 1.2 | Nenhuma: descreve o portal do desenvolvedor |
| acesso | 7 | preâmbulo, 3.1, 4.2, 5.2 (2×), 6.1, 7.1.2 | Nenhuma: sempre acesso ao Site ou à internet |
| limite | 0 | ("limitar", 6.2.1, e "limitam", 9.2, não são a palavra buscada) | — |

### Parte 2 — Termos do Diretório

- **Data:** 2026-10-16 (por volta de 23:45 UTC)
- **Quem:** mentoria (leitura e redação); revisão pela pessoa desenvolvedora em 2026-10-16
- **Fonte(s):**
  - `https://data.directory.openbankingbrasil.org.br/` e `.../participants`, acesso em 2026-10-16
  - `https://data.directory.openbankingbrasil.org.br/robots.txt`, acesso em 2026-10-16
  - Busca na web por termos de uso do Diretório (2 consultas, 2026-10-16)
- **O que foi feito:** uma leitura manual de cada endereço (raiz, `robots.txt`, `/participants`) e uma leitura só dos cabeçalhos de `/participants`. Nenhum corpo de resposta foi guardado no repositório.

| Endereço | Resposta | Observação |
|---|---|---|
| raiz `/` | HTTP 200, `application/json`, 4.514.643 bytes | Devolve a lista de participantes (mesmo conteúdo de `/participants`). Não há página HTML, rodapé nem link para termos |
| `/robots.txt` | HTTP 404 (`NoSuchKey`) | Não existe |
| `/participants` | HTTP 200, `application/json`, 4.514.643 bytes | Cabeçalhos: `Server: AmazonS3`, `Via: ... CloudFront`, `Cache-control: public, max-age=900`, `Last-Modified` cerca de 7 min antes do acesso, `ETag` presente |

Lugares onde se procurou termos de uso do Diretório **sem encontrar**:

1. raiz do domínio `data.directory.openbankingbrasil.org.br` (só JSON);
2. `robots.txt` do mesmo domínio (inexistente);
3. busca na web por "Diretório de Participantes" + "termos de uso" (resultados: termos de instituições individuais, nenhum do Diretório);
4. busca na web na wiki do Open Finance (`openfinancebrasil.atlassian.net`): apareceram os guias de operação do Diretório Central (PDF);
5. **Guia de Operação do Diretório Central, versão 1.2.14, de 28/02/2023** (152 páginas), lido em 2026-10-16 por busca de palavras no texto extraído ("termo", "uso", "automatiz", "robô", "limite", "público", "participants", "cache", "data.directory") e leitura dos trechos encontrados. Fonte: `https://openfinancebrasil.atlassian.net/wiki/download/attachments/17378602/20230228_OpenFinance-Guia_Operacao_Diretorio_Central.pdf?api=v2`. SHA-256 do PDF baixado: `ee0e4afeea886199ce593278f70e2f4fd89faa3ca6869a22121d642663a802c1`. O PDF não foi guardado no repositório. As versões de 2022 do guia não foram lidas por serem anteriores.

O que o guia diz de relevante (trechos curtos):

| Página | Trecho | Para quem |
|---|---|---|
| 14 | "Prefira por consumir dados da API Participants" | Participantes |
| 14 | "Cache local [...] é recomendável a revalidação diária dos dados" | Participantes |
| 29–31 | "Termo de Aceite" assinado via DocuSign no cadastro de usuário | Quem se cadastra no Diretório, não quem lê a lista pública |
| 43 | "Os contatos publicados no Diretório Central deverão ser utilizados apenas no contexto de implementação do Open Finance" | Todos |
| 133–134 | Suporte "por meio do Service Desk" (`https://servicedesk.openbankingbrasil.org.br/`) | Todos |

Conferência complementar: a lista pública `/participants` (2ª leitura do dia, 2026-10-16) tem 105 organizações. Os campos de cada uma não incluem contatos, e não há nenhum endereço de e-mail no arquivo.

### Parte 3 — Limite por origem e classe de frequência (pergunta 2)

- **Data:** 2026-10-16
- **Quem:** mentoria (leitura e redação); revisão pela pessoa desenvolvedora em 2026-10-16
- **Fonte(s):** wiki oficial "Área do Desenvolvedor - Open Finance Brasil" (o portal do desenvolvedor da cláusula 1.2 dos termos do Portal), lida pela API pública do Confluence (`/wiki/rest/api/content/<id>`), acesso em 2026-10-16:

| Página | URL | Versão da página | Última edição |
|---|---|---|---|
| Limites de tráfego | https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17989722 | v10 | 2025-06-13 |
| Referência | https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17957025 | v26 | 2026-06-25 |
| Limites operacionais | https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17924220/Limites+operacionais | v5 | 2025-06-13 |

- **O que foi feito:** leitura das três páginas e extração das linhas das 6 rotas do MVP na tabela "Dados Abertos / [DA] API Produtos e Serviços" da página Referência. Conferido também que as especificações fixadas (`VERSOES.md`, versão 1.0.1 das 3 famílias, SHA-256 conferido) **não** trazem classe de frequência nem limite. Nenhuma página foi copiada para o repositório.
- **Armadilha evitada:** a busca na web trouxe documentos de 2022 (Portarias 2500 e 2503, repositório da CGU) com 3 classes e mínimos de 2.000/1.000/500 TPM. Eles foram descartados por divergirem da IN 615/2025, 5.1.1, que tem 4 classes.

## Resultado

### Pergunta 1 — Portal

1. **Escopo.** Os termos valem para o "Portal do Cidadão" (1.1) e para o portal do desenvolvedor, que o "Site também compreende" (1.2). Não tratam do Diretório de Participantes nem das APIs de Dados Abertos das instituições, que ficam em outros domínios. — **Fato** (texto das cláusulas 1.1 e 1.2)
2. **O coletor não acessa o Portal.** O coletor chama o Diretório e as APIs das instituições. O Portal é lido à mão pela pessoa desenvolvedora. Por isso estes termos **não respondem** se a coleta automatizada é permitida. — **Inferência** (a partir do desenho do M1 e do escopo acima)
3. **Coleta automatizada e frequência: omisso.** Nenhuma cláusula trata de acesso automatizado, robôs ou frequência (busca acima). Omisso não significa permitido. A cláusula 9.3 diz que a tolerância a uma falha não é renúncia de direitos. — **Fato** (ausência no texto, versão de 15/07/2021)
4. **Reprodução: proibida sem autorização escrita**, salvo uso exclusivamente pessoal (7.2.1). Regra adotada: o repositório registra **dados** (ex.: "endpoint X: limite por origem não aplicável") com URL e data de acesso, além de trechos curtos citados, e **não copia páginas** do Portal (nada de captura completa, HTML ou PDF). — **Fato** (cláusula) / **Inferência** (que registrar dado com fonte não é reprodução; não é parecer jurídico)
5. **Prejuízo ao Open Finance.** A 6.2.1 veda atos que "possam causar prejuízo [...] ao Open Finance". Ela vale para o uso do Site, mas é coerente com a ética de coleta (CLAUDE.md, seção 5). — **Inferência**
6. **Governança.** Os termos são propostos pela "estrutura inicial responsável pela governança do Open Finance no Brasil" e datam de 2021. — **Hipótese:** os termos podem não refletir a governança atual. **Como testar:** identificar no Portal a entidade responsável hoje e verificar se há termos mais recentes.

### Pergunta 1 — Diretório

1. **Sem termos de uso para quem lê a lista pública.** O domínio só serve dados (JSON) e não tem `robots.txt`. O único termo citado no guia (o "Termo de Aceite") vale para quem se **cadastra** no Diretório, e o projeto não se cadastra. Resultado: **omisso** quanto a leitura automatizada da lista pública, o que não significa permitido. — **Fato** (respostas HTTP e guia v1.2.14) / **Evidência** (busca em 5 lugares)
   - **O operador recomenda revalidar a lista uma vez por dia.** O guia orienta participantes a preferir a API Participants e, se usarem cache, a fazer "revalidação diária". A recomendação é dirigida a participantes, mas é a melhor referência oficial de frequência que encontramos. — **Fato** (guia, p. 14) / **Inferência** (aplicação ao monitor)
   - **Contatos só no contexto de implementação.** A lista pública não traz contatos, então o monitor não coleta nem publica contatos. — **Fato** (guia, p. 43; conferência do arquivo)
2. **Arquivo público, servido de cache.** A lista é um arquivo estático (S3 + CloudFront) com `Cache-control: public, max-age=900`. Isso sugere que o operador espera leitura pública e frequente desse arquivo. — **Fato** (cabeçalhos) / **Inferência** (intenção do operador)
3. **Base regulatória do Diretório.** Fontes secundárias atribuem à Res. BCB 294/2023 a exigência de que o Diretório liste, por participante, as "APIs e endpoints acessíveis ao público". — **[VALIDAR]** no texto oficial do BCB antes de citar como Fato.
4. **Pergunta 1 respondida para o Diretório**, com uma ressalva: pode haver uma versão do guia mais nova que a 1.2.14 na wiki. — **[VALIDAR]**. Se a dúvida persistir, o canal oficial para perguntar é o Service Desk.

### Pergunta 2

Tabela da página Referência (v26), linhas das 3 famílias do MVP:

| Endpoint | Frequência | SLA (ms) | Timeout (s) | TPM | TPS | Limite operacional |
|---|---|---|---|---|---|---|
| GET /personal-accounts | Baixa | 4000 | 15 | 500 | 300 | NA |
| GET /business-accounts | Baixa | 4000 | 15 | 500 | 300 | NA |
| GET /personal-loans | Baixa | 4000 | 15 | 500 | 300 | NA |
| GET /business-loans | Baixa | 4000 | 15 | 500 | 300 | NA |
| GET /personal-credit-cards | Baixa | 4000 | 15 | 500 | 300 | NA |
| GET /business-credit-cards | Baixa | 4000 | 15 | 500 | 300 | NA |

1. **Classe de frequência: as 6 rotas são "Baixa".** — **Fato** (Referência, v26). A tabela não separa por versão da API. Isso responde também a V-06.
2. **Limite por origem: aplicável, quando implementado.** A página Limites de tráfego lista onde **não** se aplicam limites por origem (APIs de Segurança, Consentimento, Recursos e Serviços), e Dados Abertos não está nessa lista. Ela também diz que, em endpoints sem autenticação, a origem é o IP. — **Fato** (texto da página) / **Inferência** (aplicabilidade deduzida da lista de exceções)
3. **Não foi encontrada a marcação explícita "aplicável" ou "não aplicável" por endpoint** que a IN 615, 5.1.1, manda constar no Portal. A tabela Referência não tem essa coluna. — **Fato** (ausência nas 3 páginas lidas) / **[VALIDAR]** se existe outra página com essa marcação.
4. **Divergência no TPM.** A tabela Referência mostra **500 TPM** para as rotas "Baixa". A página Limites de tráfego e a IN 615, 5.1.1, IV, dizem **1.000 TPM** para baixa frequência. Para o projeto vale a norma (`sla.md`). A coluna da tabela parece desatualizada, já que 500 TPM era o valor de 2022. — **Fato** (os dois números) / **Inferência** (desatualização)
5. **O SLA confere com a norma.** Os 4.000 ms da tabela batem com a IN 615, 5.3.2, III, para baixa frequência. — **Fato**
6. **Dados Abertos não podem ter limite operacional mensal.** — **Fato** (Limites operacionais, v5)
7. **Margem do monitor.** O monitor faz 1 requisição a cada 15 min por endpoint, cerca de 0,07 por minuto. Isso fica pelo menos 7.500 vezes abaixo do menor valor publicado (500 TPM) e 15.000 vezes abaixo do mínimo da norma (1.000 TPM). Com isso, a Inferência do `sla.md` ("várias ordens de grandeza abaixo") fica confirmada para as 3 famílias. — **Inferência** (cálculo sobre Fatos)
8. **Timeout oficial de 15 s.** É uma referência útil para o timeout do coletor no M1, a decidir em ADR. — **Fato** (tabela) / **Opinião** (uso no coletor)

## Efeito no projeto

Portal:

- Regra de evidências: em `docs/validacoes/evidencias/` só entram URL, data de acesso, trechos curtos e, opcionalmente, o hash SHA-256 da página. Cópias completas de páginas ficam fora do git.
- Reconferir a data de revisão dos termos do Portal antes de publicar resultados (cláusula 4.1: podem mudar a qualquer momento), junto com a skill `verificacao-normativa`.
- A resposta sobre coleta automatizada depende dos termos do **Diretório** (próximo passo).

Diretório:

- **Política para `robots.txt`** (aceita pela pessoa desenvolvedora em 2026-10-16): o `robots.txt` não tem força de regra, mas o projeto o respeita. Se liberar os caminhos usados, registra-se como Evidência a favor. Se houver `Disallow` neles, o projeto não coleta esses caminhos e decide em ADR (outra fonte oficial ou pedido de autorização). Se não existir, isso é silêncio e não vale como permissão.
- **Entrada para o ADR de frequência (M1):** a lista de participantes tem cerca de 4,5 MB. Baixá-la a cada 15 min daria cerca de 430 MB por dia sem necessidade (Inferência). Proposta a decidir no ADR: consultar o Diretório **1 vez por dia**, como na "revalidação diária" que o guia recomenda aos participantes (p. 14), de preferência com requisição condicional pelo `ETag`, e manter a última lista válida quando o Diretório falhar.
- **Dados pessoais:** o monitor não coleta nem publica contatos do Diretório (guia, p. 43).
- **Canal de contato:** o Service Desk do Open Finance é o canal oficial, caso seja preciso pedir autorização ou responder a um pedido de parada (CLAUDE.md, seção 5).

Pergunta 2:

- A frequência inicial de 1 requisição a cada 15 min por endpoint fica mantida para o ADR do M1, com margem de mais de 7.500 vezes sobre qualquer limite publicado.
- O coletor deve tratar HTTP 429 como sinal de que algo está errado do lado do monitor: registrar, nunca tentar de novo em rajada. Isso é coerente com o retry do tópico 1, que só retenta 429 com backoff.
- O limite de p95 para comparação no M5 é **4.000 ms** para as 6 rotas (classe Baixa, IN 615, 5.3.2, III). Ver V-06.
- Antes de publicar, reconferir a página Referência (versão e data), porque ela muda (v26 em 2026-06-25).
