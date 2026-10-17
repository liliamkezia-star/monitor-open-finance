# V-06 — Classe de frequência de cada endpoint de Dados Abertos

- **Status:** Concluída (2026-10-16)
- **Prioridade:** Média (antes do M5; idealmente junto com a V-03)
- **Etapa / marco afetado:** A; M5 (p95 por classe)
- **Origem da pendência:** laboratório, oportunidades, seção 8

## Pergunta

Em qual classe de frequência (alta, média-alta, média, baixa) cada endpoint de Dados Abertos das famílias do MVP está classificado no Portal do Open Finance?

## Por que importa

- O limite de p95 depende da classe: 1.500, 2.000 ou 4.000 ms (IN 615, 5.3.2, I a III; `docs/normas/sla.md`, seção 2).
- A IN 615, seção 5, diz que "é necessário que cada endpoint seja classificado no Portal do Open Finance" (Fato, texto de `in615.txt`).
- Sem a classe, o projeto publica o p95 mas não o compara com nenhum limite.

## Como verificar

- Localizar no Portal a tabela de classificação; guardar URL, data e a tabela (ou trecho) usada.
- Registrar a classe por endpoint e versão, para uso como semente (seed) no dbt no M5.

## Execução

- **Data:** 2026-10-16
- **Quem:** mentoria (leitura e redação); revisão pela pessoa desenvolvedora em 2026-10-16
- **Fonte(s):** página "Referência" da Área do Desenvolvedor, https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/17957025, versão v26 (última edição em 2026-06-25), acesso em 2026-10-16
- **O que foi feito:** a mesma leitura da V-03, Parte 3. Os detalhes e a tabela completa estão em `V-03_termos-portal-limites.md`, seção "Pergunta 2".

## Resultado

| Endpoint | Classe | Limite de p95 (IN 615, 5.3.2) |
|---|---|---|
| GET /personal-accounts | Baixa | 4.000 ms (III) |
| GET /business-accounts | Baixa | 4.000 ms (III) |
| GET /personal-loans | Baixa | 4.000 ms (III) |
| GET /business-loans | Baixa | 4.000 ms (III) |
| GET /personal-credit-cards | Baixa | 4.000 ms (III) |
| GET /business-credit-cards | Baixa | 4.000 ms (III) |

- As 6 rotas das famílias do MVP são de **baixa frequência**. — **Fato** (Referência, v26)
- A tabela **não distingue versões** da API (1.0.0, 1.0.1...). — **Fato**. Se a classe mudar entre versões, a página não mostra isso. Hipótese: a classe é a mesma para todas as versões 1.0.x. Como testar: reconferir a página a cada nova versão das especificações fixadas.

## Efeito no projeto

- Semente (seed) do dbt no M5: as 6 rotas com classe "Baixa" e limite de 4.000 ms, citando a IN 615, 5.3.2, III, e a página Referência v26.
- Como todas as rotas do MVP estão na mesma classe, no MVP o "p95 por classe" se reduz a uma classe só. O painel deve dizer isso explicitamente.
- Reconferir a página Referência antes de publicar resultados.
