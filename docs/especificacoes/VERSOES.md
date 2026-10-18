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

## Nota (2026-10-18): o Diretório declara 1.1.0, que não existe no commit fixado

> Revisada em 2026-10-18. Não muda a fixação acima.

### O que o Diretório declara

**Fato (Diretório, baixado uma vez em 2026-10-18):**
- Arquivo: `https://data.directory.openbankingbrasil.org.br/participants`
- `Last-Modified: Sun, 18 Oct 2026 17:23:44 GMT`; 4.514.643 bytes; SHA-256 `d658a096674da7051748fb603444ce513d141adeced4693a08d0c58c08c2bb6b`
- 105 organizações, todas `Active`. A cópia não foi guardada no repositório.
- Contagem considerando só organizações e recursos `Active`. O Diretório separa cada família em subtipos (`ApiFamilyType`):

| `ApiFamilyType` | Recursos 1.1.0 | Recursos 1.0.1 | Organizações 1.1.0 | Organizações 1.0.1 |
|---|---|---|---|---|
| opendata-loans_personal-loans | 46 | 8 | 40 | 2 |
| opendata-loans_business-loans | 37 | 0 | 32 | 0 |
| opendata-accounts_personal-accounts | 45 | 9 | 39 | 3 |
| opendata-accounts_business-accounts | 38 | 1 | 31 | 1 |
| opendata-creditcards_personal-credit-cards | 38 | 8 | 30 | 2 |
| opendata-creditcards_business-credit-cards | 25 | 0 | 18 | 0 |
| **Total MVP** | **229 (89,8%)** | **26** | | |

Por organização, somando as três famílias do MVP, há 50 organizações:
- 45 declaram só 1.1.0;
- 2 declaram 1.1.0 e 1.0.1;
- 3 declaram só 1.0.1.

Nenhuma declara outra versão.

### O commit fixado não tem a 1.1.0

**Fato (API do GitHub, 2026-10-18):**
- `OpenBanking-Brasil/openapi` continua com `main` = `9116cf0` (o commit fixado).
- A pasta de cada família do MVP vai até `1.0.1.yml`. Não há 1.1.0 nela.

### Onde a 1.1.0 está

**Fato (API do GitHub, 2026-10-18):** a mesma organização tem um repositório por família. Cada um traz um único `swagger.yaml` e a tag `1.1.0`, uma tag leve que aponta direto para o commit. Em todos, o arquivo da `main` é igual ao da tag. O `info.version` do arquivo é `1.1.0`.

| Família | Repositório | Commit da tag `1.1.0` | Data | SHA-256 do `swagger.yaml` | Bytes |
|---|---|---|---|---|---|
| opendata-loans | `api-opendata-loans` | `bce8d251614042f26e047a43401d9b35988b804c` | 2026-04-17 | `524e432971a12fde7ae913100cc52f4451736a3d72b66797bae533183fb5e9fb` | 36300 |
| opendata-accounts | `api-opendata-accounts` | `7ab3516c69f9431a889b68f45bf1f8691da5af84` | 2026-04-10 | `0b89cfcd623f585cb847c31f3e7bfe3d5aa92e359342cdb39f39eefd25b48cd0` | 45954 |
| opendata-creditcards | `api-opendata-creditcard` (singular) | `5aa29ab281b717e6132a45ba4bef9ff4dd35cdba` | 2026-04-14 | `ba64be246fcbca32b8b0533bdd4606dd13b91d50f630e28479026a2475a7d8c3` | 37456 |

URL do arquivo numa tag: `https://raw.githubusercontent.com/OpenBanking-Brasil/<repositório>/<commit>/swagger.yaml`

**Fato:**
- Nos três repositórios, `LICENSE` na raiz dá HTTP 404 e a API do GitHub devolve `license: null`.
- A regra da V-05 vale igual: os YAMLs **não são copiados** para cá. Foram baixados só para calcular o hash.

### Leitura

- **Inferência:** para estas famílias, a fonte das versões novas passou a ser o repositório por família. O `openapi` parou na 1.0.1.
  - Evidência: último push do `openapi` em 2025-12-19; tags 1.1.0 em abril de 2026; Diretório com 1.1.0.
- **[VALIDAR]:** confirmar na documentação oficial (Área do Desenvolvedor) que esses repositórios são a fonte oficial da 1.1.0. Também ver se o `openapi` foi declarado descontinuado.
- **Hipótese:** os 26 recursos em 1.0.1 são de instituições que ainda não migraram, e não um erro de cadastro. Como testar: comparar a resposta real desses endpoints com o esquema 1.0.1 e com o 1.1.0 (M1 ou M6).

### Consequência para o projeto

Fixar só o `openapi` deixaria cerca de 90% dos recursos do MVP sem a especificação da versão que declaram. A fixação precisa passar a ter duas fontes:
- `openapi@9116cf0`, para a 1.0.1;
- o commit da tag `1.1.0` de cada repositório por família.

Isso é uma mudança de fixação. Pela regra abaixo, só entra por decisão registrada, com nova linha em "Histórico". Fica para decisão da pessoa desenvolvedora (ADR no M6 ou antes); até lá, a tabela de fixação acima não muda.

## Decisões em aberto (M6)

- **Qual versão de arquivo usar por endpoint.** As instituições registram versões no Diretório; a validação deve usar a especificação da versão que a instituição declara, não necessariamente a mais alta. Decidir em ADR no M6.
  - ~~**Hipótese**: todas as instituições do MVP declaram 1.0.x~~: **refutada em 2026-10-18**. 89,8% dos recursos do MVP declaram 1.1.0; ver a nota acima.
- **Quando mover a fixação.** Um commit novo só entra por decisão registrada (nova linha em "Histórico"), com a comparação do que mudou nos arquivos usados.

## Histórico da fixação

| Data | Commit | Motivo |
|---|---|---|
| 2026-10-10 | `9116cf0` | Fixação inicial (M0) |
