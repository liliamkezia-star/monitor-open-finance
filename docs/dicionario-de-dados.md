# Dicionário de dados

- **Situação:** esboço v0 (2026-10-29, bloco A1.3). Fica completo no M1 e vira o esquema do Parquet diário no M2 (CLAUDE.md, seção 10).
- **Base:** registro da V-02 (`scripts/v02_rodada.py`), ADR-001 (origem), ADR-002 (ciclos e lacunas), ADR-003 (timeout e fase), "pronto" do M1.

## 1. Registro de uma medição

Uma linha JSON por requisição (JSON Lines, UTF-8, fim de linha LF). Sucesso e falha usam **o mesmo formato**: o que não se aplica fica `null`, e nenhum campo some (tópico 1).

**Chave natural:** (`ciclo_utc`, `origem`, `url`). Pelo ADR-002, há no máximo uma medição por endpoint, por ciclo e por origem, e a unidade é a URL distinta, como na V-02 ("Unidade"). É essa chave que permite a recarga idempotente do M2. Ver o ponto em aberto 5 (URL de mais de uma instituição).

### 1.1 Quando e de onde

| Campo | Tipo | Nulo | Exemplo | Regra / fonte |
|---|---|---|---|---|
| `esquema_versao` | inteiro | não | `1` | Sobe a cada mudança deste formato |
| `ciclo_utc` | texto ISO 8601 | não | `"2026-10-30T12:15:00Z"` | Início do ciclo na grade de 15 min (ADR-002) |
| `timestamp_utc` | texto ISO 8601, com ms | não | `"2026-10-30T12:15:03.412Z"` | Momento **antes** da requisição (IN 615, 5.3.2, V) |
| `timestamp_brasilia` | texto ISO 8601, com fuso | não | `"2026-10-30T09:15:03.412-03:00"` | O mesmo instante no horário de Brasília. As faixas de 1 minuto da norma são no horário de Brasília (IN 615, 5.4.2, I, inf. adicionais). Calculado com o fuso `America/Sao_Paulo`, não com −3 fixo. No Windows, o `zoneinfo` precisa do pacote `tzdata` (ver ponto em aberto 6) |
| `origem` | inteiro (1, 2, 3) | não | `1` | 1 residencial no Brasil, 2 nuvem no Brasil, 3 exterior (ADR-001; V-02) |
| `coletor_versao` | texto | não | `"0.1.0+a1b2c3d"` | Versão do coletor e commit curto, para separar séries se o método mudar — **Opinião** |

### 1.2 O que foi medido

| Campo | Tipo | Nulo | Exemplo | Regra / fonte |
|---|---|---|---|---|
| `instituicao_id` | texto (UUID) | não | `"9294c0e8-…"` | `OrganisationId` do Diretório (identificador estável) |
| `instituicao_nome` | texto | sim | `"CREFISA S.A. CFI"` | `OrganisationName` do Diretório, só para leitura humana |
| `familia` | texto | não | `"opendata-loans"` | Nome da família como no `VERSOES.md` (pasta `swagger-apis/<família>`) |
| `rota` | texto | não | `"/personal-loans"` | Rota do MVP (V-06) |
| `url` | texto | não | `"https://…/opendata-loans/v1/personal-loans"` | URL exata chamada, sem parâmetros |
| `versao_api` | texto | sim | `"1.1.0"` | `ApiVersion` declarada no Diretório (V-02; nota do `VERSOES.md`) |
| `versao_major` | inteiro | não | `1` | Tirada do caminho da URL (`/v1/`). A norma mede por versão major (IN 615, 5.3.2, I, e 5.4.2, II, inf. adicionais) |
| `diretorio_etag` | texto | sim | `"\"5f1e…\""` | `ETag` da lista do Diretório usada no ciclo (ADR-002), para auditoria |

### 1.3 Resultado

| Campo | Tipo | Nulo | Exemplo | Regra / fonte |
|---|---|---|---|---|
| `categoria` | texto (lista fechada) | não | `"sucesso"` | Uma de: `sucesso`, `corpo_invalido`, `3xx`, `4xx`, `5xx`, `timeout`, `falha_conexao`. As seis da V-02 mais `3xx` (seção 4, ponto 7); o ADR-003 só muda **quando** acontece um `timeout`. `sucesso` = status 2xx com corpo JSON válido; `corpo_invalido` = status 2xx sem JSON válido. **Não** é o indicador: como cada categoria conta na disponibilidade e na conformidade fica para o ADR dos indicadores (A2.3) |
| `status` | inteiro | sim | `200` | Status HTTP; `null` quando não houve resposta (tópico 1) |
| `fase_falha` | texto (lista fechada) | sim | `"tls"` | Só em `timeout` e `falha_conexao`. Mínimo: `conexao`, `primeiro_byte`, `download`; com medição por fases: `dns`, `tcp`, `tls` no lugar de `conexao` (ADR-003, decisão 3) |
| `erro_tipo` | texto | sim | `"SSLError"` | Nome da exceção (V-02) |
| `erro_detalhe` | texto (até 300 caracteres) | sim | `"CERTIFICATE_VERIFY_FAILED …"` | Mensagem cortada (V-02) |

### 1.4 Tempos

Todos em milissegundos, número decimal. Cada fase é a **duração daquela fase**, não o tempo acumulado (o `curl -w` mostra acumulado; tópico 2).

| Campo | Tipo | Nulo | Regra / fonte |
|---|---|---|---|
| `tempo_total_ms` | decimal | sim | De antes da requisição até o último byte (IN 615, 5.3.2, V). `null` em `timeout` (ADR-003, decisão 3) e em `falha_conexao` (não houve resposta) |
| `tempo_decorrido_ms` | decimal | não | Tempo até a medição terminar, inclusive em falha. Serve para auditar o prazo de 15 s (ADR-003, gatilho "medições acima do prazo") |
| `tempo_dns_ms` | decimal | sim | Resolução do nome |
| `tempo_tcp_ms` | decimal | sim | Conexão TCP |
| `tempo_tls_ms` | decimal | sim | Negociação TLS |
| `tempo_primeiro_byte_ms` | decimal | sim | Do envio da requisição ao primeiro byte da resposta. Tempo do servidor ≈ TTFB − TCP, porque o TCP custa cerca de uma ida e volta (tópico 2) — **Inferência** |
| `tempo_download_ms` | decimal | sim | Do primeiro ao último byte |

As fases ficam `null` quando a forma de medir não as separa (ADR-003) ou quando a medição falhou antes delas.

### 1.5 Corpo da resposta

O corpo **não** é guardado, como na V-02 ("Registro"). Ficam só:

| Campo | Tipo | Nulo | Regra / fonte |
|---|---|---|---|
| `corpo_bytes` | inteiro | sim | Tamanho do corpo **depois** de descompactado (o `requests` descompacta gzip sozinho). O hash usa os mesmos bytes |
| `corpo_sha256` | texto (64 hex) | sim | Hash do corpo ("pronto" do M1). Permite ver se a resposta mudou sem guardar o conteúdo. Se o corpo tiver campos que mudam a cada chamada (data e hora, por exemplo), o hash muda sem o conteúdo mudar — **Hipótese**, a conferir no coletor v1 |
| `content_type` | texto | sim | Cabeçalho `Content-Type` |

## 2. Registro de uma lacuna

Pelo ADR-002, um ciclo que não começa (porque o anterior atrasou ou o coletor estava parado) vira lacuna e nunca é preenchido. Fica num arquivo à parte, para não misturar "não medi" com "medi e falhou".

| Campo | Tipo | Nulo | Exemplo | Regra |
|---|---|---|---|---|
| `esquema_versao` | inteiro | não | `1` | |
| `ciclo_utc` | texto ISO 8601 | não | `"2026-10-30T12:30:00Z"` | Ciclo que não aconteceu |
| `origem` | inteiro | não | `1` | |
| `motivo` | texto (lista fechada) | não | `"ciclo_anterior_atrasado"` | `ciclo_anterior_atrasado`, `coletor_parado`, `diretorio_indisponivel_sem_lista` |
| `detectado_em_utc` | texto ISO 8601 | não | `"2026-10-30T12:31:10Z"` | Quando a lacuna foi percebida |

## 3. Registro da consulta ao Diretório

Uma linha por consulta diária (ADR-002), com o `timeout=60` do ADR-003.

| Campo | Tipo | Nulo | Regra |
|---|---|---|---|
| `timestamp_utc` | texto ISO 8601 | não | |
| `status` | inteiro | sim | `200`, `304` (lista não mudou) ou outro; `null` sem resposta |
| `etag` | texto | sim | `ETag` recebido |
| `last_modified` | texto | sim | Cabeçalho `Last-Modified` |
| `organizacoes` | inteiro | sim | Quantas organizações vieram na lista |
| `usou_lista_anterior` | booleano | não | `true` quando a consulta falhou e o coletor manteve a última lista válida (ADR-002) |

## 4. Pontos em aberto e decididos

1. **Nova conexão a cada medição?** Com `requests.Session`, uma chamada ao mesmo host reaproveita a conexão (documentação do `requests`, "Keep-Alive" — **Fato**), e então DNS, TCP e TLS não acontecem. Na V-02, 3 dos 45 hosts tinham mais de uma URL, um deles com 4 (**Evidência**). Sem conexão nova, as medições do mesmo host deixam de ser comparáveis entre si. Proposta: **abrir uma conexão nova por medição**. — **Opinião**. **Decidido (2026-10-29): aceito pela pessoa desenvolvedora;** entra no coletor v1 (A1.4).
2. **Arquivo por dia em UTC ou em Brasília?** O dia da norma é o de Brasília (faixas de 00:00 a 23:59, IN 615, 5.4.2, I). Proposta para o M1: um JSONL por dia **UTC**, porque o dia da norma pode ser calculado depois pelo `timestamp_brasilia`. A partição definitiva fica para o M2. — **Opinião**
3. **Validação do corpo para a conformidade (M6)** exige o corpo ou uma validação feita na hora da coleta. Como o corpo não é guardado, isso fica para o ADR dos indicadores (A2.3) e para o M6.
4. **`versao_major` tirada da URL** supõe que todas as URLs tenham `/vN/`. As 53 URLs da V-02 (`/personal-loans`) têm `/v1/` (**Evidência**, conferido em 2026-10-29), mesmo com 45 declarando 1.1.0 e 8 declarando 1.0.1. Para as outras famílias ainda é **Hipótese**.
5. **URL de mais de uma instituição.** O ADR-002 define endpoint como "a URL de uma rota, numa versão, de uma instituição", mas a V-02 mediu uma vez por URL distinta e guardou só a primeira organização. Se duas organizações publicarem a mesma URL, medir duas vezes é carga repetida sem ganho. Proposta: medir uma vez e registrar todas as organizações que a publicam (por exemplo, `instituicao_ids` como lista). Ainda não se sabe se isso acontece. — **Hipótese**; conferir na lista do Diretório (A2.1).
6. **Fuso de Brasília no Windows.** Conferido nesta máquina: `ZoneInfo("America/Sao_Paulo")` falha com `ZoneInfoNotFoundError`, porque o Windows não traz a base de fusos e o pacote `tzdata` não está instalado (**Fato**). Proposta: acrescentar `tzdata` ao `requirements.txt` no A1.4. **Decidido (2026-10-29): aceito pela pessoa desenvolvedora.**
7. **Redirecionamentos.** O `requests` segue redirecionamentos por padrão, e aí o `status` registrado seria o da resposta final e o tempo somaria os saltos. A V-02 não registrou nenhum caso. Proposta: **não seguir** (`allow_redirects=False`) e registrar o 3xx como veio, com uma categoria nova `3xx`. Nesse caso, `sucesso` e `corpo_invalido` passam a valer só para 2xx, senão um 3xx sem JSON cairia em `corpo_invalido`. Como o 3xx conta nos indicadores fica para o A2.3. — **Opinião**. **Decidido (2026-10-29): aceito pela pessoa desenvolvedora;** a categoria `3xx` já está na seção 1.3.
