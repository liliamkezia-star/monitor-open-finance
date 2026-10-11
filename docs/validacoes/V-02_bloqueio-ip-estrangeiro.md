# V-02 — Bloqueio de IP estrangeiro pelas APIs de Dados Abertos

- **Status:** Pendente
- **Prioridade:** Média
- **Etapa / marco afetado:** A; M1 (coletor), M3 (servidor)
- **Origem da pendência:** laboratório, `07_projeto_final/2026-10-08_decisao.md`, seção 4; anexo de custo zero, seção 5

## Pergunta

Alguma instituição recusa (status, timeout ou erro de conexão) requisições às APIs de Dados Abertos vindas de IP fora do Brasil, enquanto aceita as vindas do Brasil?

## Por que importa

- Reforça (ou não) a exigência de medir do Brasil (ADR-001).
- Se houver bloqueio, medições de fora do Brasil confundiriam "bloqueio" com "indisponibilidade".

## O que já se sabe

- Em 2026-10-08, de uma origem só (provavelmente no Brasil), 7 de 8 instituições responderam HTTP 200 com JSON em `opendata-loans/personal-loans`; 1 falhou por certificado SSL inválido. Fato (laboratório, oportunidades, seção 2). As respostas não foram guardadas.

## Como verificar

- Uma rodada pequena, **uma requisição por instituição**, a partir da VM no Brasil (depois da V-01) e, se houver, de uma origem fora do Brasil; comparar status por instituição.
- A origem fora do Brasil **não** pode ser um runner do GitHub Actions (CLAUDE.md, seção 9).
- Depende de código de coleta (tópico 1). Até lá, só é possível desenhar o teste. Se for feita com `curl` manual antes do M1, registrar os comandos exatos.

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
