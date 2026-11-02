# ADR-004 — Consulta ao Diretório

- **Status:** Aceito
- **Data:** 2026-11-02
- **Marco:** M1
- **Depende de:** ADR-002 (aceito), ADR-003 (aceito); V-03 (concluída)

## Contexto

O ADR-002 (decisão 5) fixou 1 consulta por dia ao Diretório, com `ETag`, mantendo a última lista válida se ele falhar. Ao escrever essa consulta (A2.1), surgiram três perguntas que ele não responde:

- **Onde a consulta roda?** O `timeout=60` não é prazo total (ADR-003, decisão 5), então uma consulta não tem duração máxima: num teste local com `timeout=0.5` e um servidor enviando byte a byte, uma tentativa durou 4,7 s e terminou bem. — **Evidência**. O ADR-002 já prevê cerca de 14 min para um ciclo de 53 URLs no pior caso. Com a consulta no mesmo fluxo, sobram 15 min para um pior caso que não tem teto. — **Inferência**
- **A consulta retenta?** O ADR-002 proíbe retentativa na medição (decisão 4) e diz, nas alternativas, que o retry "serve para buscar dados, não para medir". Ele não trata da busca da lista. Sem retentativa, uma falha breve deixa a lista velha por mais um dia. — **Inferência**
- **O que conta como lista válida?** Um `200` com `[]` ou `{"message": ...}` é JSON válido. Sem um critério, esse corpo substituiria a lista boa. — **Fato** (testado em 2026-11-02 na primeira versão da função)

Este ADR completa a decisão 5 do ADR-002 e não substitui nenhuma das decisões dele.

## Decisão

1. **Comando separado.** A consulta é um comando próprio (`python -m coletor.diretorio`), que roda 1 vez por dia e grava o cache. O ciclo de medições só lê o cache e nunca chama o Diretório. No M1 o comando roda à mão; o agendamento fica para o M3.
2. **Até 3 tentativas, com pausas de 5 s e 10 s**, só depois de timeout, falha de conexão, corpo truncado ou 5xx. Nunca depois de 429, de outro 4xx ou de um `200` com lista inválida. Um `200` válido ou um `304` encerra a consulta do dia. A decisão 4 do ADR-002 continua valendo: uma medição nunca retenta.
3. **Lista válida** é uma lista JSON não vazia em que todo item é um objeto com `OrganisationId` em texto não vazio. Um único item ruim descarta a lista inteira, e a anterior continua valendo.
4. **Cache.** A lista, o `ETag` e `validada_em` (data da última consulta com `200` válido ou `304`) ficam em um único arquivo, gravado de forma atômica nesses dois casos. Assim o ciclo nunca lê uma lista pela metade, sabe a idade da lista, e o `ETag` de uma resposta ruim nunca faz um `304` futuro prender o coletor a uma lista antiga. Um `ETag` só é enviado se a lista correspondente tiver sido lida e validada.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Consulta numa thread, dentro do coletor | O ADR-002 diz "no M1 não há paralelismo", e duas threads dividindo o cache complicam os testes (Opinião). |
| Consulta no mesmo fluxo, em horário reservado da grade | Continua sem duração máxima e pode criar lacunas (Inferência). |
| Prazo total de relógio na consulta | Com o comando separado, a demora não atinge as medições, e o ADR-003 já decidiu que o prazo total não é necessário aqui (decisão 5). |
| Sem retentativa | Uma falha breve custaria um dia de lista velha, e a lista não é medição publicada (Opinião). |
| Aceitar a lista descartando só os itens ruins | Uma lista parcial tiraria instituições das medições sem que ninguém percebesse. Manter a anterior e registrar a falha é mais visível (Opinião). |

## Consequências

- **Positivas:**
  - Uma consulta demorada ou travada não atrasa nenhuma medição.
  - Uma falha breve do Diretório não deixa a lista velha.
  - Um `200` com lixo não apaga a lista boa.
- **Negativas:**
  - **Mais uma coisa para agendar.** Se o comando parar de rodar, a lista envelhece. O campo `validada_em` deixa o ciclo saber a idade dela, mas o que fazer com uma lista velha ainda fica para o A2.2. — **Inferência**
  - **Um arquivo de cerca de 4,5 MB é regravado a cada consulta bem-sucedida,** mesmo sem mudança na lista. O custo é irrelevante para 1 consulta por dia. — **Opinião**
  - **No Windows, a gravação falha se o ciclo estiver lendo o cache:** `os.replace` deu `PermissionError` (WinError 5) com o destino aberto, e o cache anterior ficou intacto. A falha é registrada, e a lista só é renovada na consulta seguinte. — **Evidência**
  - **Um comando travado não tem limite de duração** e pode sobrar para a execução do dia seguinte. — **Inferência**
  - **A retentativa cobre só falhas de segundos** (15 s de pausa no total). Uma queda longa ainda usa a lista anterior. — **Opinião**
  - **Uma lista válida e muito curta passa pelo critério:** um `200` com 1 organização substituiria as 105. Fica para o pente fino do A2.1.
  - **A economia do `ETag` pode não existir.** `Last-Modified` mudou de 13:53:44 para 14:08:44 entre duas consultas de 2026-11-02, junto com o `ETag`. Se o arquivo muda a cada 15 min, quase toda consulta diária baixa os 4,5 MB, e o `304` quase nunca acontece. — **Hipótese**; como testar: acompanhar o `status` e o `last_modified` do registro diário por 2 semanas, e comparar o conteúdo de duas listas seguidas.
- **O que muda no projeto:**
  - **Código:** `coletor/diretorio.py` (tentativa, retentativa, cache e comando).
  - **Dicionário de dados, seção 3:** campo novo `tentativas`.
  - **A2.2:** o ciclo lê o cache em vez de chamar o Diretório.
  - **Testes sem rede:** as 3 tentativas e as pausas, nenhuma retentativa depois de 4xx ou de lista inválida, lista inválida não substitui o cache, `ETag` de resposta ruim não é gravado, além dos casos que o ADR-002 já pede para o Diretório.

## Gatilho de revisão

- **`304` raro:** se a Hipótese acima se confirmar, rever se a requisição condicional ainda se justifica.
- **Lista parcial:** se uma lista curta passar pelo critério ou um item ruim descartar listas com frequência, rever a decisão 3.
- **Comando travado:** se isso acontecer uma vez, avaliar um prazo total para o comando.
- **M3:** ao agendar o comando na VM.

## Fontes

| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| 1 consulta por dia, `ETag`, manter a última lista válida; sem paralelismo no M1; pior caso de cerca de 14 min com 53 URLs | ADR-002, decisões 2 e 5, e Consequências | 2026-11-02 | Fato |
| `timeout=60` não é prazo total, e o prazo total não é necessário na consulta | ADR-003, decisão 5 | 2026-11-02 | Fato |
| `timeout=0.5` com uma tentativa de 4,7 s; `200` com `[]` e com objeto aceitos pela primeira versão | Testes locais contra um servidor simulado, sem rede; scripts não guardados no repositório | 2026-11-02 | Evidência |
| `os.replace` com o destino aberto dá `PermissionError` no Windows | Teste local nesta máquina (Windows 10, Python 3.12); script não guardado no repositório | 2026-11-02 | Evidência |
| `os.replace` pode falhar entre sistemas de arquivos | Documentação do Python, `os.replace` (não testado: esta máquina tem uma unidade só) | 2026-11-02 | Fato |
| 105 organizações, 4,5 MB, `Last-Modified` de 13:53:44 e 14:08:44, `ETag` diferente | 2 consultas a `https://data.directory.openbankingbrasil.org.br/participants` | 2026-11-02 | Evidência |
