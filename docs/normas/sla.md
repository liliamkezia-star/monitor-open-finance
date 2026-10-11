# Números e regras do SLA — fonte única do projeto

Todo número da norma usado em código, modelo dbt, documento ou painel vem desta tabela e cita o item. Trechos literais de `in615.txt` e `in706.txt` (ver `LEIAME.md`), extraídos em 2026-10-10. Para acrescentar uma linha, usar a skill `verificacao-normativa`.

## 1. Disponibilidade

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| Escopo: Dados Abertos incluídos | IN 615, 5.4.2 | "Cada um dos endpoints das APIs categorizadas como "Dados Abertos", "Dados Cadastrais e Transacionais", "Relatórios e Métricas", por versão, [...] deverão satisfazer os requisitos mínimos de disponibilidade abaixo" | Fato |
| **Disponibilidade diária ≥ 95%** | IN 615, 5.4.2, I | "disponibilidade diária (calendário): 95%" | Fato |
| **Disponibilidade longa ≥ 99,5%** (média móvel de 90 dias) | IN 615, 5.4.2, II | "disponibilidade longa (média móvel de 90 dias), medida diariamente: 99,5%" | Fato |
| Requisição válida | IN 615, 5.4.1 | "Serão consideradas "requisições válidas" as requisições que retornam status code da faixa 2XX, 5XX, igual a 408 ou igual a 422." | Fato |
| Sucesso × erro | IN 615, 5.4.1 | "requisições válidas com sucesso" - com status code na faixa 2XX ou igual a 422 - e "requisições válidas com erro" - com status code na faixa 5XX ou igual a 408" | Fato |
| Faixa de 1 minuto e limiar de 95% | IN 615, 5.4.1 | "Se a "disponibilidade pontual" da janela de tempo ficar abaixo de 95% isso indicará que ela será considerada como "indisponível", caso contrário será "disponível". Períodos que não tenham requisições válidas são considerados "indefinidos" e são desconsiderados para cálculo da disponibilidade." | Fato |
| Faixas no horário de Brasília | IN 615, 5.4.2, I (inf. adicionais) | "as medições devem ser feitas todos os dias, em todas as faixas de 1 minuto disponíveis, iniciando na primeira faixa (00:00:00-00:00:59) e terminando na última faixa (23:59:00-23:59:59), considerando o horário de Brasília" | Fato |
| Por versão major | IN 615, 5.4.2, II (inf. adicionais) | "as medições de disponibilidade devem ser feitas para cada versão major dos endpoints em produção" | Fato |
| Vale o ponto de vista do consumidor | IN 615, 5.4.2, IV (inf. adicionais) | "o status code a ser considerado para uma requisição é o valor reportado pelo consumidor da API" | Fato |
| Indisponibilidade programada conta | IN 615, 5.4.2, VI (inf. adicionais) | "a indisponibilidade programada não exime o cálculo da disponibilidade no período apurado" | Fato |
| Sem requisição válida → "indefinida" | IN 615, 5.4.2, VIII (inf. adicionais) | "a disponibilidade de endpoints que não tenham requisições válidas no período apurado será considerada "indefinida", não estando sujeita a um SLA" | Fato |

**Consequências para o método (a decidir em ADR do M1):**
- Com 1 requisição a cada 15 minutos, cada faixa de 1 minuto medida tem uma requisição só: a disponibilidade pontual vale 0% ou 100%, e 1.344 das 1.440 faixas do dia ficam "indefinidas". O resultado é uma **estimativa** por amostragem, não a métrica oficial. (**Inferência**)
- Falhas sem status code (timeout do cliente, erro de DNS, de TCP ou de TLS) não aparecem na lista de 5.4.1. Como contá-las é decisão de método, a ser registrada no ADR dos indicadores, com a contagem publicada à parte. (**Inferência**; decisão pendente)
- 4XX diferentes de 408 e 422 (ex.: 404, 429) ficam fora do cálculo pela regra literal. (**Fato** do texto; tratamento no ADR)

## 2. Desempenho (p95)

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| **p95 ≤ 1.500 ms** | IN 615, 5.3.2, I | "1.500ms, em endpoints classificados como de alta e média-alta frequências" | Fato |
| **p95 ≤ 2.000 ms** | IN 615, 5.3.2, II | "2.000ms, em endpoints classificados como de média frequência" | Fato |
| **p95 ≤ 4.000 ms** | IN 615, 5.3.2, III | "4.000ms, em endpoints classificados como de baixa frequência" | Fato |
| Diário | IN 615, 5.3.2 | "os endpoints das APIs deverão manter, diariamente, o percentil 95 do tempo de resposta" | Fato |
| Por versão major | IN 615, 5.3.2, I (inf. adicionais) | "as medições de tempo de resposta devem ser realizadas de maneira independente para cada versão " major " dos endpoints em produção" | Fato |
| Quais códigos entram | IN 615, 5.3.2, II (inf. adicionais) | "devem ser consideradas as requisições com todos os códigos de retorno possíveis, com exceção dos associados a limites de tráfego e limites operacionais" | Fato |
| Webhook excluído | IN 615, 5.3.2, III (inf. adicionais) | "esta subseção não se aplica às APIs de " Webhook "" | Fato |
| Medição do consumidor | IN 615, 5.3.2, V (inf. adicionais) | "a medição do tempo de resposta de cada requisição deve iniciar no momento antes da requisição ser feita e deve terminar após o último byte ser recebido, antes de qualquer processamento" | Fato |
| Vale o tempo do consumidor | IN 615, 5.3.2, VI (inf. adicionais) | "o valor do tempo de resposta a ser considerado para uma requisição é o valor reportado pelo consumidor da API" | Fato |
| Cálculo do índice do p95 | IN 615, 5.3.1, II | "o índice para o percentil 95, denotado por i 95 , é calculado pela fórmula i 95 = 0.95 ∗ n, arredondado para o número inteiro mais próximo" | Fato |
| Medição no provedor | IN 615, 5.3 | "A medição na instituição provedora da API deve iniciar quando a requisição é recebida pelo gateway e deve terminar após o último byte da resposta desta requisição ser enviado." | Fato |

**Consequências para o método:**
- A medida do consumidor (5.3.2, V) inclui a rede; a do provedor (5.3) não. Por isso o projeto publica o **p95 total** e o **p95 sem a rede** (fases de tempo separadas), com endpoint de controle e origem rotulada. (**Inferência**, método do anexo de custo zero, seção 5)
- O limite aplicável depende da **classe de frequência** de cada endpoint, definida no Portal do Open Finance (V-06). Sem ela, nenhum p95 é comparado a um limite.
- Com 96 medições por dia por endpoint, o p95 diário é estimado com poucos pontos; o intervalo de confiança é obrigatório (M5). (**Inferência**)

## 3. Limites de tráfego (ética da coleta)

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| Em Dados Abertos, a origem é o IP | IN 615, 5.1.1 | "Em APIs do tipo "Dados Abertos" a origem é o IP de onde partiu a requisição" | Fato |
| Mínimos por origem (se houver limite) | IN 615, 5.1.1, II a IV | "média-alta frequência, por endpoint e por origem, 2.000 TPM"; "média frequência [...] 1.500 TPM"; "baixa frequência [...] 1.000 TPM" (alta frequência: tabela por consentimentos, inciso I) | Fato |
| Excesso → HTTP 429 | IN 615, 5.1.1 | "As requisições que excederem os limites implementados deverão ser respondidas com status code HTTP 429 ( Too Many Requests )." | Fato |
| Aplicabilidade no Portal | IN 615, 5.1.1 | "A informação se o limite por origem é "aplicável" ou "não aplicável" deve estar explícito por endpoint no Portal do Open Finance ." | Fato |
| Vigência dos limites | IN 615, 6 (Regras transitórias) | "As mudanças realizadas na seção 5.1.1 entram em vigor a partir de 1º de setembro de 2025." | Fato |
| Capacidade global e HTTP 529 < 0,5% | IN 615, 5.1.2 | "As requisições que excederem os limites de TPS deverão ser respondidas com status code HTTP 529 ( Site is overloaded ) e o seu volume diário deve ser inferior a 0,5% das requisições válidas" | Fato |

**Consequência:** 1 requisição a cada 15 minutos por endpoint está várias ordens de grandeza abaixo de qualquer mínimo de 5.1.1 (**Inferência**). O HTTP 529 só é registrado se aparecer; nunca é provocado (CLAUDE.md, seção 5).

## 3a. Timeout

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| Timeout de 15 s (provedor e consumidor) | IN 615, 5.5 | "Padronização do timeout de tempo de resposta do provedor e do tempo de resposta do consumidor em quinze segundos." | Fato |
| Estouro no provedor → HTTP 504 | IN 615, 5.5 | "As requisições que excederem o limite de timeout do provedor deverão ser respondidas com o status code HTTP 504 ( Gateway Timeout )." | Fato |

**Consequência:** o timeout do coletor tem base normativa para ser 15 s (a confirmar no ADR do M1). (**Inferência**)

## 4. Monitoramento pela Estrutura de Governança

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| O que é monitorado | IN 706, 2.1, I a III | "tempo de resposta das APIs das instituições participantes"; "disponibilidade das APIs das instituições participantes"; "volume de requisições com status code HTTP 529" | Fato |
| Onde estão os SLAs | IN 706, 2.1 | "O Service Level Agreement (SLA) e os métodos de cálculo referentes ao tempo de resposta e à disponibilidade de APIs das instituições participantes, bem como do volume de requisições com status code HTTP 529, constam no Manual de APIs do Open Finance" | Fato |
| Aderência às especificações | IN 706, 2.2, II, a | "verificar e exigir que as APIs e artefatos associados das instituições participantes em ambiente produtivo estejam aderentes às especificações funcionais e de segurança em vigor" | Fato (texto); Inferência (inclui Dados Abertos, porque não há exceção) |
| Versões antigas no Diretório | IN 706, 2.2, IV | "a Estrutura de Governança do Open Finance deve verificar se existem versões antigas das APIs em ambiente produtivo ou cadastradas no Diretório de Participantes, de acordo com o cronograma definido pela regulamentação ou pela Estrutura de Governança do Open Finance" | Fato |
| Índice de qualidade (fora do escopo) | IN 706, V | vale para quem aderiu "ao compartilhamento de dados" e atua como "transmissora de dados" | Fato (texto); Inferência forte (não cobre Dados Abertos) |

## 5. Acesso público

| Regra | Item | Trecho literal | Rótulo |
|---|---|---|---|
| Dados permanentemente atualizados | Res. BCB 32/2020, art. 5º | "as instituições participantes devem assegurar o acesso ao público a dados mantidos permanentemente atualizados" | Fato |

## Conferência

- 2026-10-10: os trechos das seções 1 a 5 foram conferidos por script (todo trecho entre aspas existe literalmente no texto; as paráfrases estão fora de aspas) contra `in615.txt` e `in706.txt` (busca do texto literal). O trecho de 2.1 da IN 706 foi completado (o laboratório o citava com omissão). Fato.
