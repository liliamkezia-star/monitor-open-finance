# V-05 — Licença do repositório de especificações

- **Status:** Concluída (2026-10-18)
- **Prioridade:** Média (antes do M6)
- **Etapa / marco afetado:** A; M6 (conformidade), `docs/especificacoes/VERSOES.md`
- **Origem da pendência:** proposta do M0 (2026-10-10)

## Pergunta

Sob que licença ou termos as especificações de `https://github.com/OpenBanking-Brasil/openapi` podem ser usadas, baixadas e (eventualmente) redistribuídas?

## Por que importa

- Hoje o projeto **não copia** os YAMLs: baixa pelo commit fixado e confere o hash. Se houver licença permissiva, dá para incluir cópias de teste (fixtures) com segurança.

## O que já se sabe

- 2026-10-10: a API do GitHub informa `license: null`; `LICENSE` na raiz da `main` devolve HTTP 404. Fato.

## Como verificar

- Procurar no repositório (README, pastas de documentação) e no Portal do Open Finance alguma declaração de licença ou termos para as especificações.
- Se nada for encontrado, registrar "sem licença declarada" e manter a regra de não copiar.

## Execução

- **Data:** 2026-10-18
- **Quem:** mentoria (pesquisa e redação); revisão pela pessoa desenvolvedora em 2026-10-18
- **Fonte(s):** acesso em 2026-10-18
  - API do GitHub: `https://api.github.com/repos/OpenBanking-Brasil/openapi` (metadados do repositório) e `.../git/trees/9116cf09c1c371782a46280eebda4a2b59244675?recursive=1` (lista completa de arquivos do commit fixado; resposta não truncada, 1.089 itens)
  - `README.md` do commit fixado (966 bytes)
  - Os 3 YAMLs `1.0.1.yml` das famílias do MVP, baixados pelo commit fixado. SHA-256 conferido com `docs/especificacoes/VERSOES.md`
  - API do GitHub: `https://api.github.com/orgs/OpenBanking-Brasil/repos?per_page=100` (55 repositórios da organização)
  - Termos do Portal (versão de 15/07/2021), já lidos na V-03
- **O que foi feito:**
  1. Metadados do repositório: campo `license` e branch `main` (o último commit da `main` ainda é o fixado, `9116cf0`).
  2. Busca, na lista completa de arquivos do commit fixado, por nomes com "licen", "copying", "notice", "terms" ou "termo".
  3. Leitura do `README.md` e busca por "licen", "copyright" e "termo".
  4. Leitura do bloco `info` dos 3 YAMLs do MVP (campos `license`, `termsOfService` e `contact` do OpenAPI).
  5. Conferência das licenças dos outros repositórios da mesma organização.
  6. Releitura do resultado da V-03 sobre reprodução de conteúdo do Portal.

  Nenhum arquivo do repositório de especificações foi copiado para este repositório.

| Onde | O que se procurou | Resultado |
|---|---|---|
| Metadados do repositório | `license` | `null` |
| Raiz da `main` | `LICENSE` | HTTP 404 |
| Árvore do commit fixado (1.089 itens) | arquivo de licença, aviso ou termos | nenhum. Na raiz só há `README.md`, arquivos do Swagger UI, imagens e as pastas `.github`, `dictionary` e `swagger-apis` |
| `README.md` | "licen", "copyright", "termo" | nenhuma ocorrência. Ele descreve o repositório como "documentação e requisitos das APIs regulatórias" |
| `info` dos 3 YAMLs do MVP | `license`, `termsOfService` | ausentes. Só há `contact.url`, que aponta para o Service Desk do Open Finance |
| Organização `OpenBanking-Brasil` | licenças dos 55 repositórios | 53 sem licença. 2 com MIT (`suporte` e `fin_search`), que não são o repositório de especificações |

## Resultado

1. **O repositório de especificações não declara licença nem termos.** Não há declaração nos metadados, nos arquivos do commit fixado, no README nem nos YAMLs do MVP. — **Fato** (busca acima, em 2026-10-18)
2. **Sem licença, o padrão é "todos os direitos reservados".** O repositório ser público permite ler e baixar, mas não dá licença para redistribuir. — **Inferência** (regra geral de direito autoral e Termos de Serviço do GitHub, que permitem ver e fazer fork pela interface; não é parecer jurídico)
3. **A exceção da Lei 9.610, art. 8º, IV, provavelmente não cobre os YAMLs.** As especificações são publicadas pela estrutura de governança do Open Finance, que é uma entidade privada, e não pelo BCB como ato oficial. Por isso não se pode estender a elas a lógica usada para as normas em `docs/normas/LEIAME.md`. — **Inferência** `[VALIDAR]` se for preciso redistribuir algum dia
4. **O MIT de dois outros repositórios da organização não se estende a este.** A licença vale por repositório. — **Fato** (licenças informadas pela API) / **Inferência** (alcance)
5. **Os termos do Portal não resolvem a questão.** Eles proíbem a reprodução do conteúdo do Site (7.2.1, ver V-03), mas o repositório fica no GitHub, não no Site. Para o projeto isso só reforça a mesma cautela. — **Inferência**

Resposta à pergunta: **sem licença declarada.** O uso possível hoje é ler e baixar (que é o que o projeto faz). Redistribuir **não** tem base.

## Efeito no projeto

- **A regra fica como está:** os YAMLs não entram no git. O código baixa pelo commit fixado e confere o SHA-256 (`VERSOES.md`).
- **Fixtures de teste (M1 e M6):** em vez de copiar trechos dos YAMLs ou respostas reais, escrever à mão, nos testes, o **mínimo** de JSON que exercite cada caso (ex.: "200 com corpo inválido"). Fica decidido no ADR de testes do M1. — **Opinião** (proposta da mentoria)
- **Se um dia for preciso redistribuir** (ex.: publicar uma cópia de referência), o caminho é pedir autorização pelo Service Desk (o `contact.url` dos próprios YAMLs) e registrar a resposta aqui como "Reconferência".
- **Reconferir antes do M6:** a licença do repositório pode mudar. Basta repetir os passos 1 a 4.
