# V-02 — Bloqueio de IP estrangeiro ou de nuvem pelas APIs de Dados Abertos

- **Status:** Pendente — desenho ampliado em 2026-10-18 (três origens; revisado pela pessoa desenvolvedora em 2026-10-18)
- **Prioridade:** Média
- **Etapa / marco afetado:** A; M1 (coletor), M3 (servidor)
- **Origem da pendência:** laboratório, `07_projeto_final/2026-10-08_decisao.md`, seção 4; anexo de custo zero, seção 5

## Pergunta

1. Alguma instituição recusa (status, timeout ou erro de conexão) requisições às APIs de Dados Abertos vindas de IP fora do Brasil, enquanto aceita as vindas do Brasil?
2. Alguma instituição recusa requisições vindas de IP de **nuvem** (datacenter) no Brasil, enquanto aceita as vindas de IP residencial no Brasil?

A pergunta 2 foi acrescentada em 2026-10-18, durante o passo 2 da V-01. As duas regiões possíveis da VM (São Paulo e Vinhedo) ficam no Brasil, então a comparação "Brasil × exterior" sozinha não detectaria um bloqueio de IP de nuvem.

## Por que importa

- Reforça (ou não) a exigência de medir do Brasil (ADR-001).
- Se houver bloqueio, medições de fora do Brasil confundiriam "bloqueio" com "indisponibilidade".
- **O coletor 24/7 vai rodar numa VM de nuvem (M3).** Se uma instituição bloquear IP de nuvem, o monitor registraria como "indisponível" uma API que está no ar para clientes comuns. Isso inverteria a conclusão do projeto para aquela instituição.

## O que já se sabe

- Em 2026-10-08, de uma origem só (provavelmente no Brasil), 7 de 8 instituições responderam HTTP 200 com JSON em `opendata-loans/personal-loans`; 1 falhou por certificado SSL inválido. Fato (laboratório, oportunidades, seção 2). As respostas não foram guardadas.
- Que algumas instituições bloqueiem IP de datacenter (independentemente do país) é uma **Hipótese**. Como testar: a comparação entre as origens 1 e 2 abaixo.

## Como verificar

Uma rodada por origem, **uma requisição por instituição**, na mesma rota e, de preferência, no mesmo dia:

| # | Origem | Quando | O que isola |
|---|---|---|---|
| 1 | Computador da pessoa desenvolvedora (IP residencial, Brasil) | Antes da VM, com o script local (tópico 1 dominado) | Referência: o que um cliente comum no Brasil vê |
| 2 | VM Oracle (IP de nuvem, Brasil) | Perto do início do M3, logo depois de criar a VM (V-01, "Plano") | Bloqueio de IP de nuvem (comparada com a 1) |
| 3 | Fora do Brasil, se houver uma origem permitida | Opcional | Bloqueio por país (comparada com a 2) |

Leitura dos resultados:

- Falha em 2 e sucesso em 1: indício de bloqueio de IP de nuvem.
- Falha em 3 e sucesso em 2: indício de bloqueio por país.
- Falha em todas as origens testadas: problema da instituição, não bloqueio.
- **Uma falha isolada não prova bloqueio.** Para confirmar, repete-se a rodada **em outro horário ou dia**, nunca com retentativa logo em seguida. Cada rodada continua com uma requisição por instituição.
- Erro de SSL (como o de 2026-10-08) não é bloqueio. Por isso o registro guarda o **tipo** do erro.

Cada registro de uma rodada tem: timestamp em UTC, **origem** (1, 2 ou 3), identificador estável da instituição no Diretório, URL exata chamada, rota, categoria do resultado (sucesso, 4xx, 5xx, timeout, falha de conexão; 200 só conta como sucesso com corpo JSON válido), status HTTP (`None` sem resposta) e tipo do erro. Sem tempos por fase (tópico 2) e sem guardar o corpo da resposta. A lista do Diretório é baixada uma vez por rodada, e a rota escolhida é a publicada pelo maior número de instituições (contagem registrada). O timeout é de 15 s (página "Referência" da wiki do Open Finance, v26; ver V-03).

Regras que continuam valendo:

- A origem fora do Brasil **não** pode ser um runner do GitHub Actions (CLAUDE.md, seção 9).
- O tópico 1 está dominado desde 2026-10-17, então a rodada da origem 1 pode ser feita com o script local. Se alguma rodada for feita com `curl` manual, registrar os comandos exatos.

Não fazer: repetir requisições em sequência, varrer endpoints, usar proxies ou VPNs de terceiros sem ler os termos.

## Execução

- **Data:**
- **Quem:**
- **Fonte(s):**
- **O que foi feito:**

## Resultado

—

## Efeito no projeto

—
