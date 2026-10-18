# V-02 — Bloqueio de IP estrangeiro ou de nuvem pelas APIs de Dados Abertos

- **Status:** Em andamento — origem 1 feita em 2026-10-18 (53/53 com sucesso); origem 2 perto do M3; origem 3 opcional
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

- **Data:** 2026-10-18. Origem 1 feita; origens 2 e 3 pendentes.
- **Quem:**
  - Script `scripts/v02_rodada.py`, escrito pelo Claude e revisado pela pessoa desenvolvedora (modo "Claude escreve, ela revisa", CLAUDE.md seção 6).
  - As duas rodadas foram executadas pelo Claude, a pedido dela, no computador dela.
- **Fonte(s):** Diretório (`/participants`, `Last-Modified: Sun, 18 Oct 2026 17:38:44 GMT`, nas duas rodadas). Raiz ICP-Brasil v10: `https://acraiz.icpbrasil.gov.br/credenciadas/RAIZ/ICP-Brasilv10.crt`.
- **O que foi feito:**
  - **Rota:** `/personal-loans` (`opendata-loans`). É a família com mais instituições.
  - **Unidade:** uma requisição por **URL distinta**, e não por instituição. Algumas organizações publicam várias marcas, cada uma com a sua URL (Bradesco/Losango/Next, XP/Rico/Clear/Modal, Carrefour/Atacadão/Sam's Club). Com isso, 53 URLs de 42 organizações. Só entram organizações e recursos `Active`.
  - **Formato e registro:** JSON Lines, uma linha por requisição. O nome do arquivo é a hora de início em UTC + a origem. Os registros ficam no git, em `docs/validacoes/evidencias/V-02/`, para auditoria. Sem retentativa; pausa de 1 s entre requisições; timeout de 15 s; User-Agent identifica o projeto.

| Rodada | Arquivo | Início – fim (UTC) | Raízes confiáveis | Sucesso | Falha de conexão | SHA-256 |
|---|---|---|---|---|---|---|
| 1 | `2026-10-18T1740Z_origem1.jsonl` | 17:40:52 – 17:42:36 | só `certifi` (lista da Mozilla) | 43 | 10 | `e243478481a5f3d39bdb0b48cb4e51ab1f553c34fd776605c6f4b97e954efe39` |
| 2 | `2026-10-18T1745Z_origem1.jsonl` | 17:45:52 – 17:47:26 | `certifi` + raiz ICP-Brasil v10 | 53 | 0 | `470ad33e0aaea1716a6eb273844aa124a4853a0f1df0d3317fb8091c3b7be742` |

Nenhuma resposta 4xx, 5xx, timeout ou corpo inválido nas duas rodadas.

## Resultado

**Origem 1 (residencial, Brasil): todas as 53 URLs responderam HTTP 2xx com JSON válido** (rodada 2). Esta é a referência para comparar com a origem 2.

**As 10 falhas da rodada 1 não eram bloqueio.**
- **Fato:** todas foram `SSLError` com `CERTIFICATE_VERIFY_FAILED`:
  - Bradesco ×4 (Bradesco, Bradesco Financiamentos, Losango, Next);
  - Inter;
  - Caixa;
  - QI Tech;
  - PagSeguro;
  - Sicoob;
  - InfinitePay.
- **Fato (`openssl`, 2026-10-18):** as 10 cadeias de certificado terminam na **Autoridade Certificadora Raiz Brasileira v10 (ICP-Brasil)**. Na maioria, a intermediária é a AC SOLUTI SSL EV G4. A lista de raízes da Mozilla, usada pelo `certifi`, não inclui essa raiz.
- **Fato:** o SHA-256 da raiz baixada do ITI (certificado em DER) é igual ao da raiz enviada por `api.bradesco.com`: `6e0bff069a26994c15de2c4888cc54af84882e5495b7fbf66be9ccffec7489f6`. A raiz vale até 2032-07-01.
- **Evidência:** com essa raiz acrescentada (rodada 2), as mesmas 10 URLs responderam com sucesso, cinco minutos depois.
- **Inferência:** a falha de "certificado SSL inválido" de 2026-10-08, no laboratório, provavelmente tinha a mesma causa. Não dá para confirmar, porque as respostas não foram guardadas.

As perguntas 1 e 2 continuam **sem resposta**: dependem das origens 2 (VM, perto do M3) e 3 (opcional).

## Efeito no projeto

- **O coletor (M1) precisa confiar na raiz ICP-Brasil v10, além do `certifi`.** Sem isso, cerca de 1 em cada 5 URLs (10 de 53) apareceria como "indisponível" por um problema do nosso lado. O monitor erraria justamente nos maiores bancos. Desligar a verificação (`verify=False`) não é opção.
- O hash da raiz fica fixado no código. Se não bater, a rodada para antes de medir (mesma regra das especificações em `VERSOES.md`).
- **Ponto de atenção (Hipótese):** se uma instituição migrar para outra raiz ICP-Brasil (por exemplo, uma v11), a falha volta como `SSLError`. Como testar: o coletor registra o tipo do erro, e um `SSLError` novo pede checar a cadeia com `openssl` antes de concluir que a API está indisponível.
- Próxima rodada: origem 2, a partir da VM, com o mesmo script e as mesmas raízes.
