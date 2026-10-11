# Especificações oficiais — versão fixada

A régua de conformidade (M6) são as especificações OpenAPI oficiais do Open Finance Brasil. Este arquivo fixa **qual** versão o projeto usa, para que o resultado seja reproduzível.

## Fonte

- Repositório: https://github.com/OpenBanking-Brasil/openapi, pasta `swagger-apis/`.
- **Fato (API do GitHub, 2026-10-10):** o repositório não tem tags nem releases; a branch padrão é `main`; o último push é de 2025-12-19.
- **Fato (2026-10-10):** não há arquivo `LICENSE` na raiz (HTTP 404). Por isso os YAMLs **não são copiados** para este repositório (ver V-05).

## Fixação

| Campo | Valor |
|---|---|
| Commit fixado | `9116cf09c1c371782a46280eebda4a2b59244675` |
| Data do commit | 2025-12-19T19:58:04Z |
| Mensagem | Merge pull request #371 from Sensedia/release-variable-incomes-19122025 |
| Data da fixação | 2026-10-10 |

Como baixar um arquivo fixado:
`https://raw.githubusercontent.com/OpenBanking-Brasil/openapi/<commit>/swagger-apis/<família>/<arquivo>`

Regra: o código só usa arquivos cujo SHA-256 bate com a tabela abaixo. Se não bater, para com erro (não valida contra um arquivo diferente em silêncio).

## Inventário das famílias do MVP no commit fixado

SHA-256 calculado em 2026-10-10 sobre o arquivo baixado pela URL acima.

| Família | Arquivo | SHA-256 | Bytes |
|---|---|---|---|
| opendata-loans | 1.0.0-beta.1.yml | `e299289bff2e67dd0ee0394141cc7b237706c9de9ff68cb60d7e91c885113616` | 33233 |
| opendata-loans | 1.0.0-beta.2.yml | `fe677e9bd98009df3c560cc82fac57b785f418605bda4fd6931c312fc5b1bd8a` | 35526 |
| opendata-loans | 1.0.0-rc.1.yml | `315a3e4af44e3d4016a51ed9b3fba0ae6c2cd4000c756f1c71dcaa14c57b71ca` | 35521 |
| opendata-loans | 1.0.0.yml | `1e3a7b6bec506ace0f017be4a15ce13603acc180d41f9d91085c3e58bb70eb6d` | 36769 |
| opendata-loans | **1.0.1.yml** | `ad9beba80b2d29de9d05ca89ac8c2fbbf1e602493927ff9fe7337869adab544a` | 35494 |
| opendata-accounts | 1.0.0-beta.1.yml | `fa1a6db026de0042cc9b20e8396a85d9d192e76b532cf26f963b0f0a5efe92cb` | 44223 |
| opendata-accounts | 1.0.0-beta.2.yml | `a164a0cb6ca2f65bb44516ec87ee4eac1f24f8d144d6735753de8e04b8aee9e6` | 45099 |
| opendata-accounts | 1.0.0-rc.1.yml | `0171a2408f23bcb187fdcc594c50cec889fe1fcf75ec1b3267e35dd378761817` | 46408 |
| opendata-accounts | 1.0.0.yml | `b49af957649204c1bfde52b780da4bfb2edf88ba8db0ce1fe8a8ec4ddb13399c` | 46403 |
| opendata-accounts | **1.0.1.yml** | `3783e7e447e0baa728aa29db649149d5b540c6da06d96f24af26382b9419b350` | 44745 |
| opendata-creditcards | 1.0.0-beta.1.yml | `244668e1b128171a5ef7c78606c0409d5dfa7a4f5b841c511fc9409e4ed281b7` | 32649 |
| opendata-creditcards | 1.0.0-beta.2.yml | `34a51d3aaa479397d6ff2780654039faea62cd958cb48e7cba572be3a1fcbc36` | 36979 |
| opendata-creditcards | 1.0.0-rc.1.yml | `9e169a6ff55000fc5618ffda95cd2961afb25dec252874f78abf945ba2ef4f1f` | 36974 |
| opendata-creditcards | 1.0.0.yml | `19dda67bb83d6331b3d07e4f94dce176d5e22afad08725f93d74e880a49d52e9` | 37925 |
| opendata-creditcards | **1.0.1.yml** | `19e4bfc3b7d147eaf58913b8dcd1b7db352a8bb422edcc5e53f69cdbaf404bd3` | 36487 |

Em negrito, a versão mais alta de cada família no commit fixado.

## Decisões em aberto (M6)

- **Qual versão de arquivo usar por endpoint.** As instituições registram versões no Diretório; a validação deve usar a especificação da versão que a instituição declara, não necessariamente a mais alta. Decidir em ADR no M6. (**Hipótese**: todas as instituições do MVP declaram 1.0.x; como testar: cruzar as versões do Diretório com a tabela acima no M1.)
- **Quando mover a fixação.** Um commit novo só entra por decisão registrada (nova linha em "Histórico"), com a comparação do que mudou nos arquivos usados.

## Histórico da fixação

| Data | Commit | Motivo |
|---|---|---|
| 2026-10-10 | `9116cf0` | Fixação inicial (M0) |
