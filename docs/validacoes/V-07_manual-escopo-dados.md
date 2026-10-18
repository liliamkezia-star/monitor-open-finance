# V-07 — Manual de Escopo de Dados e Serviços 8.0 (IN 759)

- **Status:** Concluída (2026-10-18; 1 item `[VALIDAR]` registrado: Resolução Conjunta nº 1/2020)
- **Prioridade:** Média (antes do M1)
- **Etapa / marco afetado:** A; escopo do MVP (3 famílias), `docs/normas/`
- **Origem da pendência:** busca de vigência de 2026-10-10 (`docs/normas/LEIAME.md`)

## Pergunta

O Manual de Escopo de Dados e Serviços do Open Finance, versão 8.0 (IN BCB 759, de 2026-07-09), define quais APIs de Dados Abertos são obrigatórias e para quais instituições?

## Por que importa

- **Hipótese:** se definir, ele é a base normativa para dizer que uma instituição "deveria" expor um endpoint, e para tratar a ausência de um endpoint no Diretório de forma diferente de uma indisponibilidade.
- Como testar: ler o texto integral e procurar "Dados Abertos" e os nomes das famílias do MVP.

## Como verificar

- Baixar o texto integral pela API de normativos do BCB (procedimento em `docs/normas/LEIAME.md`).
- Se for relevante, adicionar a norma a `docs/normas/` (texto, JSON bruto, hash, linha no LEIAME) e os itens usados a `sla.md`.
- Confirmar a vigência na mesma busca.

## Execução

- **Data:** 2026-10-18
- **Quem:** mentoria (pesquisa e redação); revisão pela pessoa desenvolvedora em 2026-10-18
- **Fonte(s):** API de normativos do BCB (procedimento em `docs/normas/LEIAME.md`), acesso em 2026-10-18:
  - texto integral da IN 759: `exibenormativo?p1=Instrução Normativa BCB&p2=759`, guardado em `docs/normas/brutos/in759.json` e `docs/normas/in759.txt`
  - texto integral da IN 724 (versão 7.0, a que vale até 2/11/2026), só para comparar. **Não** foi guardada
  - busca de vigência "Manual de Escopo de Dados", guardada em `docs/normas/brutos/busca_2026-10-18_manual-escopo.json`
- **O que foi feito:**
  1. Download do texto integral da IN 759 e conversão para `.txt` pelo mesmo método das outras normas. Para conferir o método, ele foi aplicado à IN 706 baixada no mesmo dia: o resultado ficou **idêntico** ao `in706.txt` já guardado, e o JSON bruto também é idêntico.
  2. Leitura do preâmbulo, dos artigos, da Introdução e da seção 3 ("Dados sobre produtos e serviços disponíveis à contratação"). Busca no texto por "dados abertos", "obrigat", "facultativ", "endpoint", "Diretório", "S1", "segmento" e "Resolução Conjunta".
  3. Busca de vigência ordenada por data.
  4. Comparação da Introdução e da seção 3 entre a IN 724 (7.0) e a IN 759 (8.0).

## Resultado

### Vigência

1. **A IN 759 só entra em vigor em 3/11/2026** ("Art. 3º Esta Instrução Normativa entra em vigor em 3 de novembro de 2026."). Até lá vale a **IN 724** (versão 7.0, de 16/4/2026, em vigor desde a publicação, DOU de 22/4/2026), que a IN 759 revoga (art. 2º). — **Fato**
2. Na busca de 2026-10-18, a IN 759 é a versão mais nova do Manual de Escopo e aparece com `Revogado=0`. A IN 724 também aparece com `Revogado=0`, porque a revogação só vale a partir de 3/11. — **Evidência**
3. **Para o MVP, a diferença entre as versões não importa.** A 8.0 só acrescenta a portabilidade de crédito (seção 8, "Sumário das alterações"). A Introdução e a seção 3 são **iguais** nas duas versões; a única diferença são 2 caracteres invisíveis (espaço de largura zero) dentro de uma palavra da 3.1. — **Fato** (comparação dos textos)

### Pergunta: o manual define quais APIs de Dados Abertos são obrigatórias?

1. **Define os dados obrigatórios, não as APIs.** O manual lista os **dados** de produtos e serviços que precisam ser compartilhados: "Os dados listados neste manual são de implementação obrigatória, de acordo com a Circular nº 4.015, de 2020". As APIs (endpoints) ficam por conta das especificações técnicas do Portal: "orientações detalhadas de caráter técnico deverão ser disponibilizadas no Portal". — **Fato** (Introdução)
2. **As 3 famílias do MVP correspondem a seções obrigatórias da seção 3:** — **Fato** (títulos das seções) / **Inferência** (correspondência com as famílias)

| Família do MVP | Seção do manual | Título no manual |
|---|---|---|
| `opendata-accounts` | 3.1 | Contas de depósitos à vista, de poupança e de pagamento pré-pagas |
| `opendata-creditcards` | 3.2 | Contas de pagamento pós-pagas ("conta de pagamento pós-paga (cartão)") |
| `opendata-loans` | 3.3.2 | Empréstimos |

3. **A única exceção explícita em Dados Abertos fica fora do MVP:** "No momento, é facultativa a implementação de endpoint para o compartilhamento dos dados relativos aos terminais de autoatendimento de terceiros compartilhados" (2.4.2, canais de atendimento). Nada parecido aparece nas seções 3.1, 3.2 e 3.3.2. — **Fato**
4. **Campos opcionais não são escolha livre.** Quando a especificação marca um dado como opcional, as instituições "somente poderão deixar de encaminhar os dados para os quais houver impossibilidade devido à sua inexistência, não havendo discricionaridade nesse encaminhamento". — **Fato** (Introdução). Isso importa para a conformidade no M6.

### Pergunta: para quais instituições?

5. **O manual não diz.** Ele é "de observância obrigatória por parte das instituições participantes" (art. 1º), mas não define quem precisa participar. Não aparece nenhuma menção a segmento (S1, S2…) nem ao Diretório. Ele remete à **Resolução Conjunta nº 1/2020**, que "estabelece a obrigatoriedade de compartilhamento de dados de produtos e serviços", e à **Circular nº 4.015/2020**, que "disciplina o escopo desses dados". — **Fato** (ausência e remissões no texto)
6. Quem é obrigado a participar (e, portanto, a expor Dados Abertos) está, provavelmente, na Resolução Conjunta nº 1/2020. — **Inferência** `[VALIDAR]`: ler o texto oficial da Resolução Conjunta 1 (artigos sobre participação obrigatória e voluntária) antes de citar.
7. Uma instituição que entra voluntariamente também precisa compartilhar os dados do manual (art. 1º fala em "instituições participantes", sem distinção). — **Inferência** (depende do item 6)

Resposta à hipótese: **confirmada em parte.** O manual é a base normativa para dizer que **os dados** das 3 famílias são obrigatórios para as instituições participantes. Ele **não** basta, sozinho, para dizer **quais instituições** deveriam expor cada endpoint.

## Efeito no projeto

- **Norma nova em `docs/normas/`:** `in759.txt` e `brutos/in759.json`, com hash e vigência no `LEIAME.md`. A IN 724 não foi guardada: ela perde a vigência em 3/11/2026 e a seção usada é igual. Se algum resultado for publicado com data anterior a 3/11/2026, citar a IN 724 como a versão vigente naquela data.
- **Linguagem (M5/M6):** um endpoint ausente no Diretório **não** é indisponibilidade. Ele só pode ser descrito como "dado obrigatório sem endpoint publicado" depois do `[VALIDAR]` do item 6. Até lá, usar só "endpoint não publicado no Diretório", sem juízo de obrigação.
- **`sla.md`:** nada a acrescentar. O manual não traz números de disponibilidade nem de tempo de resposta.
- **Pendência nova:** ler a Resolução Conjunta nº 1/2020 (participação obrigatória). Pode virar um item desta V-07 ("Reconferência") ou uma validação própria. A decisão é da pessoa desenvolvedora.
