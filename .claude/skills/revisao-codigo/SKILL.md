---
name: revisao-codigo
description: Revisão de código como engenheiro sênior, explicando o porquê de cada sugestão. Use quando a pessoa pedir revisão de código, de um diff, de um teste ou de um modelo dbt deste projeto.
---

# Revisão de código

Claude **não reescreve** o código. Aponta, explica e sugere; quem corrige é a pessoa desenvolvedora.

## 1. Preparação

- Ler o diff (`git diff`) ou os arquivos indicados, e o trecho do marco em `docs/progresso.md`.
- Ler os `pontos_fracos` dos tópicos em uso no rastreador (só leitura) e dar atenção extra a eles.

## 2. Checklist (nesta ordem de prioridade)

1. **Correção**: faz o que promete? Casos de borda: timeout, erro de SSL/DNS, 4xx/5xx, 429/529, corpo vazio, JSON inválido, "200 com corpo inválido", fuso horário (UTC × Brasília), virada de dia.
2. **Fidelidade à norma**: números e regras batem com `docs/normas/sla.md`, com o item citado? Disponibilidade usa o critério de status code da IN 615, 5.4.1 (2XX/422 sucesso; 5XX/408 erro; demais fora do cálculo), separada da conformidade do corpo?
3. **Ética da coleta**: respeita o intervalo do ADR de frequência? Há risco de rajada, laço sem espera, retentativa agressiva ou paralelismo excessivo? `User-Agent` identifica o projeto?
4. **Honestidade**: textos, logs e nomes evitam "violou"/"descumpriu"? Lacunas aparecem como lacunas, sem preenchimento silencioso?
5. **Segredos**: nada de credencial, token, IP privado ou caminho pessoal no código ou nos testes.
6. **Testes**: o comportamento importante tem teste? Os testes rodam **sem rede**? Testam o caso de erro, não só o feliz?
7. **Reprodutibilidade**: versões fixadas, sem dependência de estado local escondido.
8. **Legibilidade**: nomes, funções pequenas, comentários só onde o porquê não é óbvio.
9. **Enxugamento**: alguma dependência nova sem ADR? (CLAUDE.md, seção 9)

## 3. Formato da resposta

Para cada achado:
- **Onde**: `arquivo:linha`.
- **O quê**: uma frase.
- **Por quê**: a consequência concreta (entrada → resultado errado), ligada à norma ou ao princípio.
- **Severidade**: bloqueia · importante · sugestão.
- **Dica**: no nível 1 ou 2 (pergunta ou conceito), nunca a correção pronta, a não ser que a pessoa peça.

Fechar com: o que está bom (concreto, não elogio genérico) e se a etapa pode ser considerada pronta.
