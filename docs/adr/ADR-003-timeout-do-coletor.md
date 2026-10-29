# ADR-003 — Timeout do coletor

- **Status:** Aceito
- **Data:** 2026-10-29
- **Marco:** M1
- **Depende de:** ADR-002 (aceito); V-03 (concluída)

## Contexto

O coletor precisa saber quanto tempo esperar por uma resposta antes de desistir. Esse número afeta três coisas: o que conta como falha, a duração máxima de um ciclo (o ADR-002 usa 15 s no cálculo do pior caso) e o p95, porque uma resposta lenta que é cortada deixa de ser um tempo e vira uma falha.

O que já se sabe:

- **A norma fixa 15 s para os dois lados.** "Padronização do timeout de tempo de resposta do provedor e do tempo de resposta do consumidor em quinze segundos." Se o provedor estourar, ele responde HTTP 504. — **Fato** (IN 615, 5.5; `sla.md`, seção 3a)
- **A página Referência confirma 15 s** para as 6 rotas do MVP. — **Fato** (V-03, pergunta 2; Referência v26)
- **O tempo do consumidor vai do momento antes da requisição até o último byte recebido.** — **Fato** (IN 615, 5.3.2, V)
- **O timeout do `requests` não é um prazo total.** O valor vale separadamente para conectar e para cada espera **entre** bytes, e a documentação avisa: "Neither the connect nor read timeouts are wall clock". O timeout de conexão vale para cada endereço IP tentado, então um servidor com IPv4 e IPv6 pode dobrar o tempo percebido. — **Fato** (documentação do `requests`, "Advanced Usage", seção "Timeouts", versão `latest`; o projeto fixa a 2.34.2)
- **A resolução de nomes (DNS) fica fora do timeout.** No `urllib3` 2.8.0 (o instalado com o `requests` 2.34.2), a função `create_connection` chama `socket.getaddrinfo` sem prazo e só depois aplica o timeout ao socket. — **Fato** (código-fonte de `urllib3/util/connection.py`, conferido em 2026-10-29)
- Nas duas rodadas da V-02 (origem 1, 53 URLs), nenhuma requisição estourou o timeout. — **Evidência** (V-02, "Resultado"). Ressalva: o script usou `timeout=15` do `requests`, que não é o prazo total decidido aqui.

## Decisão

1. **Timeout de medição: prazo total de 15 s de relógio**, contado como na IN 615, 5.3.2, V: do momento antes da requisição até o último byte do corpo. Inclui DNS, TCP, TLS, espera pelo primeiro byte e download. A norma não diz se o timeout do consumidor inclui o DNS. Usar para o timeout a mesma janela da medição do tempo é **Inferência**, e aplicar ao monitor um valor escrito para consumidores regulados também é **Inferência**.
2. **O coletor controla esse prazo por conta própria**, sem depender só do parâmetro `timeout` do `requests` (que não é um prazo total e não cobre o DNS). Ao passar de 15 s, a medição é interrompida.
3. **Uma medição interrompida é registrada como `timeout`**, com status `None`, a **fase** em que estourou e o tempo decorrido. Ela **não** é um tempo de resposta de 15 s. O mínimo de fases é: conexão (DNS + TCP + TLS), primeiro byte e download. A separação de DNS, TCP e TLS depende da forma de medir escolhida no M1 (com `socket` e `ssl`, como no tópico 2, sai a separação; só com o `requests`, não sai).
4. **HTTP 504 é outra coisa.** Um 504 é uma resposta do provedor (5xx), registrado com status e tempo normais, e não é um timeout do coletor.
5. **Diretório: `timeout=60` do `requests`** (conexão e espera entre bytes; não é prazo total). A lista tem cerca de 4,5 MB, é baixada 1 vez por dia (ADR-002) e não é medição publicada, então um prazo total não é necessário. — **Opinião**. Se estourar, vale a regra do ADR-002 (manter a última lista válida).
6. **Como contar um `timeout`** na disponibilidade e no p95 fica para o ADR dos indicadores (M1). Este ADR só define quando ele acontece e como é registrado.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Não decidir agora | O ADR-002 usa 15 s no cálculo do pior caso de um ciclo, e o coletor do M1 precisa de um valor. |
| `requests.get(url, timeout=15)` sozinho | Não é prazo total e não cobre o DNS (documentação do `requests`; código do `urllib3`). Uma resposta que manda 1 byte a cada 14 s pode levar muito mais que 15 s sem estourar, e o pior caso do ciclo no ADR-002 deixa de valer. |
| Timeout menor, por exemplo 4 s (o limite do p95 da classe Baixa) | Cortaria respostas lentas que chegam dentro do prazo da norma. O p95 medido ficaria artificialmente baixo, e uma API lenta mas no ar viraria falha (Inferência). |
| Timeout maior, por exemplo 30 s | A norma diz que o consumidor espera 15 s (IN 615, 5.5). Esperar mais mediria algo que nenhum consumidor regulado vê, e quase dobraria o pior caso do ciclo (31 s contra 16 s por URL; ADR-002). |
| Registrar o timeout como tempo de 15 s | Misturaria falha com tempo. O tempo real da resposta é desconhecido (é "mais de 15 s"), e pôr 15 s no lugar puxaria o p95 para um valor inventado (Inferência). |

## Consequências

- **Positivas:**
  - O critério de desistência é o mesmo da norma e o da página Referência.
  - O pior caso do ciclo no ADR-002 (15 s + 1 s de pausa por URL) passa a ser controlado pelo coletor, e não apenas esperado (desde que o DNS também seja limitado; ver Negativas).
  - Com a fase registrada, dá para separar "não conectou" de "conectou e o servidor não respondeu" (tópico 2).
- **Negativas (obrigatório):**
  - **Mais código.** Garantir um prazo total exige controle próprio (por exemplo, `stream=True` com conferência do relógio durante o download, ou medição por fases com `socket` e `ssl`, como no tópico 2). Isso é mais código e mais teste do que um `timeout=15`.
  - **O DNS precisa de tratamento à parte.** O `getaddrinfo` não tem prazo (Contexto, Fato) e é uma chamada bloqueante. Para limitá-lo, o coletor precisa resolver o nome fora do fluxo principal, por exemplo numa thread com prazo. — **Inferência**. Se a resolução travar, a thread pode continuar presa depois que a medição já foi registrada como `timeout`. — **Hipótese**. **Como testar:** no M1, um teste com resolução de nome lenta (mock) e, na VM, a conferência de que nenhuma medição passa de 15 s mais uma pequena folga.
  - **Respostas pouco acima de 15 s viram falha.** Uma resposta que chegaria em 15,5 s conta como `timeout`. Isso segue a norma, mas pesa numa amostra de 96 por dia (ADR-002).
  - **O timeout pode vir do lado do monitor.** Uma rede doméstica ruim (origem 1) gera timeouts que não são culpa da instituição. O endpoint de controle e a origem registrada ajudam a separar os dois casos (`sla.md`, seção 2; ADR-001).
- **O que muda no projeto:**
  - **M1:** o coletor tem prazo total de 15 s e registra `timeout` com a fase e o tempo decorrido. Os testes sem rede cobrem: DNS lento (resolução que passa do prazo); timeout na conexão; timeout no primeiro byte; download lento que passa de 15 s no total mesmo sem nenhuma espera de 15 s entre bytes; 504 registrado como 5xx e não como `timeout`; Diretório com prazo de 60 s.
  - **ADR dos indicadores (M1):** decide como `timeout` entra na disponibilidade (a lista de 5.4.1 não tem esse caso) e se fica fora do p95.

## Gatilho de revisão

- **Mudança na norma ou na página Referência:** se a IN 615, 5.5, ou o timeout da tabela Referência mudar, ou se uma rota nova do MVP tiver outro valor.
- **Timeouts frequentes de uma instituição:** se mais de 5% das medições de uma instituição em 7 dias forem `timeout` na mesma fase, investigar antes de publicar (pode ser bloqueio de origem, V-02). O limiar de 5% é **Opinião**, a recalibrar com os dados do M4.
- **Medições acima do prazo:** se a conferência na VM mostrar medições que passaram de 15 s mais a folga, a implementação do prazo é revista (ver o tratamento do DNS nas Negativas).

## Fontes

| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| Timeout de 15 s do provedor e do consumidor; estouro do provedor → HTTP 504 | IN 615, 5.5, via `docs/normas/sla.md`, seção 3a | 2026-10-10 | Fato |
| 15 s na página Referência para as 6 rotas do MVP | V-03, pergunta 2 (Referência v26) | 2026-10-16 | Fato |
| Tempo do consumidor: de antes da requisição até o último byte | IN 615, 5.3.2, V, via `sla.md`, seção 2 | 2026-10-10 | Fato |
| O timeout do `requests` vale para conexão e para a espera entre bytes; não é prazo total; conexão por endereço IP | https://requests.readthedocs.io/en/latest/user/advanced/#timeouts | 2026-10-29 | Fato |
| Versão do `requests` no projeto: 2.34.2 (com `urllib3` 2.8.0 instalado) | `requirements.txt`; ambiente local | 2026-10-29 | Fato |
| `getaddrinfo` é chamado sem prazo, antes do timeout do socket | `urllib3/util/connection.py`, função `create_connection` (`urllib3` 2.8.0) | 2026-10-29 | Fato |
| O timeout do consumidor cobre a mesma janela da medição do tempo, com DNS; vale para o monitor | IN 615, 5.5 e 5.3.2, V (a norma não diz) | 2026-10-10 | Inferência |
| Nenhum timeout nas rodadas da origem 1 (com `timeout=15` do `requests`) | V-02, "Resultado"; `docs/validacoes/evidencias/V-02/` | 2026-10-18 | Evidência |
| Lista do Diretório com cerca de 4,5 MB; timeout de 60 s no script da V-02 | V-03, parte 2; `scripts/v02_rodada.py` | 2026-10-16 / 2026-10-18 | Fato |
| Uma thread de DNS travada pode continuar presa depois do `timeout` | — (a testar no M1) | — | Hipótese |
