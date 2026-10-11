# V-08 — Termos do GitHub Actions: uso como coletor

- **Status:** Concluída (herdada do laboratório)
- **Prioridade:** — (reconferir antes do M7)
- **Etapa / marco afetado:** A; regra do CLAUDE.md, seção 9; M7 (CI e publicação)
- **Origem:** laboratório, `07_projeto_final/2026-10-08_anexo_custo-zero.md`, seção 1

## Pergunta

Os termos do GitHub permitem rodar o coletor 24/7 em runners hospedados pelo GitHub?

## Execução

- **Data:** 2026-10-08 (no laboratório)
- **Fonte:** GitHub Terms for Additional Products and Features, https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features (acessada em 2026-10-08)

## Resultado

Não. Nos runners hospedados pelo GitHub, os termos proíbem "Any other activity unrelated to the production, testing, deployment, or publication of the software project" e citam como exemplo de violação o uso como "serverless application infrastructure". — **Rótulo:** Fato (texto); Inferência (um coletor 24/7 cai no exemplo proibido).

Outros fatos do mesmo anexo, relevantes para o M7: uso gratuito em repositório público com runners padrão; agendamento com intervalo mínimo de 5 minutos e atrasos no início de cada hora; agendamentos desativados após 60 dias sem atividade no repositório.

## Efeito no projeto

- Regra: **GitHub Actions só para CI e publicação do site estático; nunca para coleta** (CLAUDE.md, seção 9).
- A coleta roda na VM da etapa A.

## Reconferência

- **Pendente: reconferir antes do M7** (os termos mudam sem aviso). Registrar aqui data, URL e trecho literal.
