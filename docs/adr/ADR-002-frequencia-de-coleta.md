# ADR-002 — Frequência de coleta

- **Status:** Aceito
- **Data:** 2026-10-29
- **Marco:** M1
- **Depende de:** V-03 (concluída), V-06 (concluída), ADR-001 (aceito); ADR do timeout (M1, ainda não aberto)

## Contexto

O "pronto" do M1 exige que o coletor "respeita o intervalo do ADR de frequência" (CLAUDE.md, seção 10). O valor inicial de **1 requisição a cada 15 minutos por endpoint** vem do laboratório e ficou à espera da V-03 (CLAUDE.md, seção 5). A V-03 e a V-06 já foram concluídas, então dá para fixar o valor agora.

Restrições:

- **Limites por origem.** Em Dados Abertos, a origem é o IP. O mínimo da norma para baixa frequência é 1.000 TPM, e as 6 rotas do MVP são de classe "Baixa". — **Fato** (IN 615, 5.1.1, IV; V-06). A página Referência mostra 500 TPM, menos que a norma. — **Fato** (V-03, pergunta 2, item 4)
- **Termos.** Os termos do Portal são omissos sobre coleta automatizada, e o Diretório não tem termos para a lista pública. Omisso não significa permitido. — **Fato** (V-03, pergunta 1)
- **Diretório.** A lista de participantes tem cerca de 4,5 MB e vem com `ETag` e `max-age=900`. O guia do Diretório recomenda aos participantes a "revalidação diária". — **Fato** (V-03, parte 2; guia v1.2.14, p. 14)
- **Métrica oficial.** A disponibilidade oficial usa todas as requisições de cada faixa de 1 minuto (IN 615, 5.4.1). Qualquer frequência viável para um monitor externo dá uma **estimativa** por amostragem, nunca a métrica oficial. — **Fato** (norma) / **Inferência** (aplicação; `sla.md`, seção 1)
- **Duração de uma rodada.** Em sequência, com pausa de 1 s e timeout de 15 s, as 53 URLs de `/personal-loans` levaram cerca de 1 min 44 s (rodada 1) e 1 min 34 s (rodada 2), contando do primeiro ao último registro. — **Evidência** (V-02, arquivos `.jsonl` da origem 1)

## Decisão

1. **Instituições: 1 requisição a cada 15 minutos por endpoint.** "Endpoint" aqui é a URL de uma rota, numa versão, de uma instituição. Isso dá 96 medições por dia por endpoint.
2. **Ciclos em grade fixa (UTC):** os ciclos começam em :00, :15, :30 e :45, e dentro de cada ciclo as requisições são feitas **em sequência**, com pausa de 1 s entre elas. No M1 não há paralelismo.
3. **Nunca há sobreposição de ciclos.** Se um ciclo não terminar até o horário do próximo, o próximo não começa. O horário perdido é registrado como lacuna e nunca é preenchido depois (CLAUDE.md, seção 10, M4).
4. **Sem retentativa dentro da medição.** Cada medição é uma tentativa só. Depois de uma falha, a próxima tentativa é a do ciclo seguinte, então a taxa por endpoint nunca passa de 1 a cada 15 min. Um **HTTP 429** é registrado e tratado como sinal de erro do lado do monitor, nunca como motivo para retentar.
5. **Diretório: 1 consulta por dia**, com requisição condicional pelo `ETag` (`If-None-Match`). Se o Diretório falhar, o coletor mantém a última lista válida e registra a falha.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Não decidir agora | O "pronto" do M1 depende deste ADR (CLAUDE.md, seção 10). |
| 1 a cada 5 min (ou menos) | O ganho de precisão nas estimativas é pequeno em relação ao triplo de requisições para cada instituição (Inferência). Os termos são omissos, e a regra do projeto é frequência modesta (CLAUDE.md, seção 5). O ciclo de 3 famílias ficaria apertado sem paralelismo (ver Consequências). |
| 1 a cada 30 ou 60 min | O p95 diário sairia de 48 ou 24 pontos, contra 96. Com 24, o índice do p95 cai entre os 2 maiores valores do dia (IN 615, 5.3.1, II: i95 = 0,95 × n), e o intervalo de confiança do M5 fica largo demais para ser útil (Inferência). |
| Retentar na hora quando falha (backoff do tópico 1) | Esconde a falha que o monitor quer medir e aumenta a taxa justamente quando a API está mal. O retry do tópico 1 serve para buscar dados, não para medir (Inferência). |
| Paralelismo desde o M1 | Não é preciso com 1 família (ver Duração), e o risco de rajada contra uma mesma instituição é maior (CLAUDE.md, seção 5). Fica como gatilho de revisão para as 3 famílias. |
| Diretório a cada ciclo (15 min) | Seriam cerca de 430 MB por dia sem necessidade, e o próprio operador recomenda revalidação diária (V-03, "Efeito no projeto"). |
| Ciclo começando quando o anterior termina (sem grade) | O intervalo real varia com a duração do ciclo, e as medições deixam de cair em horários comparáveis entre dias (Opinião). |

## Consequências

- **Positivas:**
  - A taxa por endpoint fica em cerca de 0,07 requisição por minuto, pelo menos 7.500 vezes abaixo do menor limite publicado (500 TPM) e 15.000 vezes abaixo do mínimo da norma (V-03, pergunta 2, item 7). — **Inferência** (cálculo sobre Fatos)
  - Sem retentativa e sem sobreposição, o coletor nunca aumenta a carga sobre uma API que está falhando.
  - O Diretório é baixado no máximo uma vez por dia, e menos que isso quando o `ETag` não muda.
- **Negativas (obrigatório):**
  - **A disponibilidade fica muito longe da métrica oficial.** Por dia, 96 das 1.440 faixas de 1 minuto têm uma medição e as outras 1.344 ficam "indefinidas". Cada faixa medida vale 0% ou 100%. Quedas curtas entre dois ciclos não são vistas (`sla.md`, seção 1). — **Inferência**
  - **O p95 diário vem de no máximo 96 pontos.** Com i95 = 0,95 × 96 ≈ 91, o p95 é o 91º valor ordenado e fica sensível a poucas medições lentas. O intervalo de confiança é obrigatório no M5. — **Fato** (fórmula) / **Inferência** (sensibilidade)
  - **Um ciclo pode estourar os 15 minutos.** No pior caso, com todas as URLs no timeout, o tempo é de N × (15 s + 1 s): 53 URLs dariam cerca de 14 min, perto do limite, e as cerca de 154 do MVP completo dariam cerca de 41 min. Nos dias normais, extrapolando a V-02, 154 URLs levariam por volta de 5 min (Inferência). Por isso o MVP com 3 famílias (M7) precisa reabrir esta decisão.
  - **Lista do Diretório desatualizada por até 1 dia.** Uma instituição que entra ou muda de URL só é medida no dia seguinte (Inferência).
  - **Falhas transitórias contam como falha.** Sem retentativa, uma falha de rede de 1 segundo vira uma medição com erro. Isso é coerente com a norma, que vale "o valor reportado pelo consumidor" (IN 615, 5.4.2, IV), mas pesa mais numa amostra de 96 (Inferência).
- **O que muda no projeto:**
  - **M1:** o coletor tem a grade de 15 min, faz o ciclo em sequência com pausa de 1 s, não retenta, registra 429 e lacunas, e consulta o Diretório 1 vez por dia com `ETag`. Os testes sem rede cobrem: nenhuma retentativa depois de timeout, de 5xx ou de 429; um ciclo atrasado não sobrepõe o seguinte; o Diretório com falha mantém a última lista; `304 Not Modified` reaproveita a lista em cache.
  - **M4:** o orquestrador segue a mesma grade (DAG a cada 15 min, `max_active_runs=1`), e lacuna é lacuna.
  - **M5:** o método do intervalo de confiança parte de n ≤ 96 por dia e por endpoint.
  - **CLAUDE.md, seção 5:** "valor inicial" passa a "valor fixado no ADR-002".

## Gatilho de revisão

- **Ciclo longo:** se a duração do ciclo passar de 10 min em mais de 1% dos ciclos de uma semana, ou antes de ligar as 3 famílias (M6/M7). A opção a estudar é paralelismo **entre** instituições, com no máximo 1 requisição por vez por host.
- **HTTP 429:** qualquer 429 recebido abre uma investigação. Mais de um 429 da mesma instituição em 7 dias reabre este ADR para aquela instituição.
- **Pedido de uma instituição** para reduzir ou parar a coleta (CLAUDE.md, seção 5).
- **Termos:** se os termos do Portal ou do Diretório passarem a tratar coleta automatizada ou frequência (reconferir antes de publicar; V-03).
- **M5:** se o intervalo de confiança do p95 ou da disponibilidade ficar largo demais para sustentar qualquer conclusão com 96 pontos.

## Fontes

| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| Valor inicial de 15 min, à espera da V-03 | CLAUDE.md, seção 5; `docs/origem.md` | 2026-10-08 (laboratório) | Fato |
| Em Dados Abertos a origem é o IP; mínimo de 1.000 TPM para baixa frequência | IN 615, 5.1.1 e 5.1.1, IV, via `docs/normas/sla.md`, seção 3 | 2026-10-10 | Fato |
| As 6 rotas do MVP são de classe "Baixa"; 500 TPM na página Referência | V-03, pergunta 2; V-06 (Referência v26) | 2026-10-16 | Fato |
| Margem de mais de 7.500 vezes | V-03, pergunta 2, item 7 | 2026-10-16 | Inferência |
| Termos do Portal omissos; Diretório sem termos para a lista pública | V-03, pergunta 1 | 2026-10-16 | Fato |
| Diretório: cerca de 4,5 MB, `ETag`, `max-age=900`; "revalidação diária" | V-03, parte 2; guia do Diretório Central v1.2.14, p. 14 | 2026-10-16 | Fato |
| Disponibilidade oficial por faixas de 1 minuto; faixas sem requisição válida são "indefinidas" | IN 615, 5.4.1 e 5.4.2, VIII, via `sla.md`, seção 1 | 2026-10-10 | Fato |
| 1.344 de 1.440 faixas indefinidas; estimativa por amostragem | `sla.md`, seção 1, "Consequências para o método" | 2026-10-10 | Inferência |
| Vale o status reportado pelo consumidor | IN 615, 5.4.2, IV, via `sla.md`, seção 1 | 2026-10-10 | Fato |
| Índice do p95: i95 = 0,95 × n | IN 615, 5.3.1, II, via `sla.md`, seção 2 | 2026-10-10 | Fato |
| Rodadas de 53 URLs em cerca de 1 min 34 s e 1 min 44 s (sequencial, pausa de 1 s, timeout de 15 s) | `docs/validacoes/evidencias/V-02/2026-10-18T1740Z_origem1.jsonl` e `…T1745Z_origem1.jsonl` (primeiro e último registro); V-02, "Execução" | 2026-10-18 | Evidência |
| Cerca de 154 endpoints no MVP completo | CLAUDE.md, seção 5 | 2026-10-08 (laboratório) | Inferência |
