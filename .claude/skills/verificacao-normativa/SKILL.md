---
name: verificacao-normativa
description: Verifica e cita a norma antes de usar qualquer número, limite ou regra do Open Finance (SLA, p95, disponibilidade, limites de tráfego, monitoramento). Use sempre que um número da norma for entrar em código, modelo dbt, documento ou painel, e antes de publicar resultados.
---

# Verificação normativa

## 1. Localizar

- Procurar o item em `docs/normas/sla.md`. Se estiver lá, usar a citação dali.
- Se não estiver: procurar no texto integral (`docs/normas/in615.txt`, `in706.txt`, `res32.txt`) e copiar o **trecho literal**, com o item exato (ex.: "IN 615, 5.4.1").
- Nunca citar de memória. Se o texto local não tiver o item, dizer "não encontrado no texto local" e indicar a fonte oficial (API de normativos do BCB).

## 2. Conferir a vigência

Obrigatório antes de publicar resultados e, no mínimo, a cada marco.
- Consultar a busca de normativos do BCB (procedimento em `docs/normas/LEIAME.md`).
- Conferir se a IN 615 (Manual de APIs 7.0) e a IN 706 (Manual de Monitoramento 3.0) seguem com `Revogado=0` e se não há versão posterior de cada manual.
- Rotular o resultado como **Evidência** (campo da busca), não como confirmação formal.
- Se houver versão nova: parar, avisar, baixar o texto novo para `docs/normas/`, comparar os itens usados e propor um ADR se algum número mudar.

## 3. Registrar

- Item novo usado: adicionar linha em `docs/normas/sla.md` (número · item · trecho literal · onde é usado no projeto), com ok prévio.
- Conferência de vigência: adicionar linha no histórico de `docs/normas/LEIAME.md`.

## 4. Interpretação

- Separar o que o texto diz (**Fato**) do que concluímos dele (**Inferência**). Ex.: "a IN 706, 2.2, II, a não distingue tipos de API" é Fato; "portanto cobre Dados Abertos" é Inferência.
- Quando o texto remeter a outro lugar (ex.: "classificado no Portal do Open Finance"), registrar a remissão e abrir uma validação em `docs/validacoes/` se o dado ainda não foi verificado.
