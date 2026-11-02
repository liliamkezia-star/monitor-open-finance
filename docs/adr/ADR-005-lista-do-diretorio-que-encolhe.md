# ADR-005 — Lista do Diretório que encolhe

- **Status:** Aceito
- **Data:** 2026-11-02
- **Marco:** M1
- **Depende de:** ADR-004 (aceito)

## Contexto

O critério de lista válida do ADR-004 (decisão 3) olha o formato, não o tamanho. Um `200` com 1 organização válida substituía as 105 da lista anterior, e o ciclo passaria a medir uma instituição só, sem nenhum aviso. — **Fato** (testado em 2026-11-02, no pente fino do A2.1)

O ADR-004 deixou isso como consequência negativa e como gatilho de revisão ("lista parcial"). Este ADR completa a decisão 3 dele e não a substitui.

## Decisão

Uma lista válida com **menos da metade** das organizações da lista em cache é recusada: o cache continua como está, e o registro leva `erro_tipo` `ListaEncolheu`, `organizacoes` com o que veio e `usou_lista_anterior` verdadeiro. O comando sai com 0, porque há lista válida em cache. Exatamente a metade é aceita, e sem lista anterior não há comparação.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Só registrar e aceitar a lista | A lista curta já estaria em uso quando alguém lesse o registro, e as medições das outras instituições teriam parado (Inferência). |
| Limite em número fixo de organizações | Fica velho conforme o Diretório muda; a comparação com a lista anterior se ajusta sozinha (Opinião). |
| Limite mais apertado, como 90% | A lista tem 105 organizações, e não há histórico para saber quanto ela varia de um dia para outro. Um limite apertado recusaria mudanças reais (Opinião). |

## Consequências

- **Positivas:**
  - Uma lista parcial não tira a maioria das instituições das medições.
- **Negativas:**
  - **Se a lista encolher de verdade para menos da metade, o coletor fica na antiga** até alguém olhar o registro. Como o comando sai com 0, o agendador não avisa. — **Inferência**
  - **A metade é um número escolhido sem dados:** uma queda de 105 para 53 ainda passa. — **Opinião**
- **O que muda no projeto:**
  - **Código:** `consultar_diretorio`, em `coletor/diretorio.py`.
  - **Dicionário de dados, seção 3:** novo valor de `erro_tipo`.
  - **Testes sem rede:** recusa abaixo da metade, aceite na metade exata e sem lista anterior.
  - **O ADR dos indicadores** do A2.3 passa a ser o ADR-006.

## Gatilho de revisão

- **`ListaEncolheu` no registro:** qualquer ocorrência pede uma conferência manual da lista.
- **Histórico:** depois de 2 semanas de registro diário, rever o limite com a variação real de `organizacoes`.

## Fontes

| Afirmação | Fonte (URL ou arquivo, seção) | Data de acesso | Rótulo |
|---|---|---|---|
| Critério de lista válida e gatilho "lista parcial" | ADR-004, decisão 3 e "Gatilho de revisão" | 2026-11-02 | Fato |
| Um `200` com 1 organização substituía as 105 | Teste local do comando com resposta simulada; script não guardado no repositório | 2026-11-02 | Fato |
| A lista tem 105 organizações | `data/diretorio/consultas.jsonl` (2026-11-02) | 2026-11-02 | Evidência |
