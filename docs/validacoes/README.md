# Validações

Cada pendência `[VALIDAR]` vira um registro aqui: o que foi verificado, como, com que fonte, em que data e com que resultado. Um registro concluído não é reescrito; uma reconferência acrescenta uma seção "Reconferência AAAA-MM-DD".

## Índice

| ID | Pergunta | Etapa | Prioridade | Status |
|---|---|---|---|---|
| [V-01](V-01_oracle-a1-regiao-brasil.md) | Há VM Ampere A1 Always Free disponível em São Paulo ou Vinhedo? | A (M0 → M3) | **Alta — semana de 12/10** | Pendente |
| [V-02](V-02_bloqueio-ip-estrangeiro.md) | As APIs de Dados Abertos bloqueiam IP estrangeiro? | A | Média | Pendente |
| [V-03](V-03_termos-portal-limites.md) | Termos de uso do Portal e do Diretório; limites por origem para Dados Abertos | A (M0 → M1) | **Alta — semana de 12/10** | **Concluída (2026-10-16)** |
| [V-04](V-04_bigquery-carga-lote.md) | A carga em lote no BigQuery é gratuita? | B (antes do M9) | Baixa | Pendente |
| [V-05](V-05_licenca-especificacoes.md) | Qual é a licença do repositório de especificações? | A (antes do M6) | Média | Pendente |
| [V-06](V-06_classe-frequencia-endpoints.md) | Qual é a classe de frequência de cada endpoint de Dados Abertos? | A (antes do M5) | Média | **Concluída (2026-10-16)** |
| [V-07](V-07_manual-escopo-dados.md) | O Manual de Escopo de Dados 8.0 (IN 759) define as APIs de Dados Abertos obrigatórias? | A (antes do M1) | Média | Pendente |
| [V-08](V-08_termos-github-actions.md) | Os termos do GitHub permitem usar o Actions como coletor? | A | — | **Concluída (herdada)** |

## Modelo

```markdown
# V-NN — <pergunta curta>

- **Status:** Pendente | Em andamento | Concluída | Bloqueada
- **Prioridade:** Alta | Média | Baixa
- **Etapa / marco afetado:** ...
- **Origem da pendência:** <arquivo e seção onde o [VALIDAR] apareceu>

## Pergunta
<a pergunta exata, respondível com sim/não ou com um valor>

## Por que importa
<o que muda no projeto conforme a resposta>

## Como verificar
<passos; fonte oficial a consultar; o que NÃO fazer (ex.: nada de teste de carga)>

## Execução
- **Data:**
- **Quem:**
- **Fonte(s):** <URL + data de acesso; arquivo de evidência, se guardado>
- **O que foi feito:**

## Resultado
<resposta> — **Rótulo:** Fato | Evidência | Inferência | Hipótese

## Efeito no projeto
<ADR aberto, marco ajustado, regra nova no CLAUDE.md, nada>
```

Evidências brutas (capturas, respostas HTTP) podem ir para `docs/validacoes/evidencias/V-NN/`, **sem dados pessoais e sem segredos** (nada de número de cartão, e-mail ou OCID de conta).
