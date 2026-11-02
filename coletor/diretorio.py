"""Consulta a lista de participantes do Diretório.

Comando separado, que roda 1 vez por dia e grava o cache que o ciclo de medições lê
(ADR-004): python -m coletor.diretorio
Sai com 0 se terminar com uma lista válida em cache, mesmo que seja a anterior, e
com 1 se não houver lista nenhuma ou se não conseguir gravar.

A consulta não é medição: serve para saber o que medir (ADR-002, decisão 5, e
ADR-003, decisão 5). Por isso usa `requests`, e não as fases de `coletor.py`.
A retentativa também só existe aqui: uma medição nunca retenta (ADR-002, decisão 4).
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from coletor.coletor import RAIZ_REPO, USER_AGENT, formatar_utc

DIRETORIO_URL = "https://data.directory.openbankingbrasil.org.br/participants"
TIMEOUT_S = 60  # conexão e espera entre bytes; não é prazo total (ADR-003, decisão 5)
PAUSAS_S = (5, 10)  # uma pausa entre cada duas tentativas: 3 tentativas no máximo
ARQUIVO_CACHE = RAIZ_REPO / "data" / "diretorio" / "participantes.json"
ARQUIVO_CONSULTAS = RAIZ_REPO / "data" / "diretorio" / "consultas.jsonl"

# Falhas que podem passar sozinhas. ChunkedEncodingError é o corpo truncado:
# a resposta foi interrompida no caminho, e o conteúdo não chegou a ser avaliado.
ERROS_DE_REDE_RETENTAVEIS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
)


def motivo_lista_invalida(dados):
    """Devolve por que `dados` não serve como lista de participantes, ou None se serve."""
    if not isinstance(dados, list):
        return f"raiz do JSON é {type(dados).__name__}, não lista"
    if not dados:
        return "lista vazia"
    for posicao, organizacao in enumerate(dados):
        if not isinstance(organizacao, dict):
            return f"item {posicao} não é objeto"
        identificador = organizacao.get("OrganisationId")
        if not isinstance(identificador, str) or not identificador:
            return f"item {posicao} sem OrganisationId"
    return None


def fazer_uma_tentativa(url=DIRETORIO_URL, etag_cache=None):
    """Faz um GET no Diretório e devolve sempre o mesmo dicionário.

    `status`, `etag`, `last_modified` e `organizacoes` seguem a seção 3 do
    dicionário de dados. `lista` só é preenchida quando a lista é válida:
    é o único caso em que a lista e o `etag` podem ir para o cache.
    """
    resultado = {
        "status": None,
        "etag": None,
        "last_modified": None,
        "organizacoes": None,
        "lista": None,
        "erro_tipo": None,
        "erro_detalhe": None,
        "deve_retentar": False,
    }

    cabecalhos = {"User-Agent": USER_AGENT}
    if etag_cache:
        cabecalhos["If-None-Match"] = etag_cache

    try:
        resposta = requests.get(url, headers=cabecalhos, timeout=TIMEOUT_S)
    except ERROS_DE_REDE_RETENTAVEIS as erro:
        resultado["erro_tipo"] = type(erro).__name__
        resultado["erro_detalhe"] = str(erro)
        resultado["deve_retentar"] = True
        return resultado
    except requests.exceptions.RequestException as erro:
        # Ex.: excesso de redirecionamentos. Tentar de novo não resolve.
        resultado["erro_tipo"] = type(erro).__name__
        resultado["erro_detalhe"] = str(erro)
        return resultado

    resultado["status"] = resposta.status_code
    resultado["etag"] = resposta.headers.get("ETag")
    resultado["last_modified"] = resposta.headers.get("Last-Modified")

    if resposta.status_code == 304:
        return resultado

    if resposta.status_code != 200:
        resultado["erro_tipo"] = "StatusInesperado"
        resultado["erro_detalhe"] = f"HTTP {resposta.status_code}"
        resultado["deve_retentar"] = 500 <= resposta.status_code < 600
        return resultado

    try:
        # json.loads nos bytes, e não resposta.json(): fora de UTF-8, o .json() tenta
        # adivinhar a codificação e corrompe o texto sem avisar.
        dados = json.loads(resposta.content)
    except (ValueError, RecursionError) as erro:
        # ValueError cobre JSONDecodeError e UnicodeDecodeError; aninhamento fundo dá
        # RecursionError.
        resultado["erro_tipo"] = type(erro).__name__
        resultado["erro_detalhe"] = "corpo não é JSON válido"
        return resultado

    motivo = motivo_lista_invalida(dados)
    if motivo:
        resultado["erro_tipo"] = "ListaInvalida"
        resultado["erro_detalhe"] = motivo
        return resultado

    resultado["lista"] = dados
    resultado["organizacoes"] = len(dados)
    return resultado


def buscar_com_retentativa(
    url=DIRETORIO_URL,
    etag_cache=None,
    pausas=PAUSAS_S,
    fetcher=fazer_uma_tentativa,
    sleeper=time.sleep,
):
    """Tenta até `len(pausas) + 1` vezes e devolve o resultado da última tentativa.

    Só tenta de novo quando `deve_retentar` é verdadeiro. A chave `tentativas` diz
    quantas foram feitas. `fetcher` e `sleeper` existem para os testes sem rede.

    A duração não tem limite, porque `TIMEOUT_S` não é prazo total. Por isso esta
    função não pode rodar no mesmo fluxo das medições.
    """
    tentativas = 1
    resultado = fetcher(url, etag_cache)
    for pausa in pausas:
        if not resultado["deve_retentar"]:
            break
        sleeper(pausa)
        tentativas += 1
        resultado = fetcher(url, etag_cache)
    resultado["tentativas"] = tentativas
    return resultado


def motivo_cache_invalido(dados):
    """Devolve por que `dados` não serve como cache, ou None se serve."""
    if not isinstance(dados, dict):
        return f"raiz do JSON é {type(dados).__name__}, não objeto"

    etag = dados.get("etag")
    if etag is not None and not isinstance(etag, str):
        return "etag não é texto"

    validada_em = dados.get("validada_em")
    if not isinstance(validada_em, str):
        return "validada_em não é texto"
    try:
        instante = datetime.fromisoformat(validada_em)
    except ValueError:
        return "validada_em não é uma data ISO 8601"
    if instante.utcoffset() is None:
        return "validada_em sem fuso"

    return motivo_lista_invalida(dados.get("lista"))


def ler_cache(caminho=ARQUIVO_CACHE):
    """Lê o cache e devolve sempre o mesmo dicionário.

    Sem cache utilizável, `etag`, `validada_em` e `lista` vêm None: um `ETag` sem a
    lista correspondente nunca pode ser enviado, porque um 304 deixaria o coletor
    sem lista. `problema` separa os dois casos: fica None quando o arquivo não existe
    (normal na primeira execução) e explica o erro quando ele existe e não serve.
    """
    vazio = {"etag": None, "validada_em": None, "lista": None, "problema": None}
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return vazio
    except (OSError, ValueError, RecursionError) as erro:
        # ValueError cobre JSONDecodeError e UnicodeDecodeError.
        return {**vazio, "problema": f"{type(erro).__name__}: {erro}"}

    motivo = motivo_cache_invalido(dados)
    if motivo:
        return {**vazio, "problema": motivo}

    return {
        "etag": dados.get("etag"),
        "validada_em": dados["validada_em"],
        "lista": dados["lista"],
        "problema": None,
    }


def gravar_cache(etag, lista, validada_em, caminho=ARQUIVO_CACHE):
    """Grava o cache de forma atômica (ADR-004, decisão 4).

    O temporário fica na mesma pasta do destino, porque `os.replace` falha entre
    unidades, e tem nome único, para dois comandos não escreverem no mesmo arquivo.
    O `fsync` garante que os dados estão no disco antes da troca de nome.

    Levanta `OSError` se não conseguir gravar: no Windows, isso acontece se outro
    processo estiver com o destino aberto. O cache anterior continua intacto, e
    quem chama decide o que registrar.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    descritor, temporario = tempfile.mkstemp(
        dir=caminho.parent, prefix=f"{caminho.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descritor, "w", encoding="ascii") as arquivo:
            # ASCII: o json.dump escapa todo o resto, inclusive surrogates soltos,
            # que quebrariam uma gravação em UTF-8.
            json.dump(
                {"etag": etag, "validada_em": validada_em, "lista": lista}, arquivo
            )
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        # Depois de uma troca bem-sucedida, o temporário já não existe.
        Path(temporario).unlink(missing_ok=True)


def agora_utc():
    return datetime.now(timezone.utc)


def consultar_diretorio(
    caminho_cache=ARQUIVO_CACHE,
    caminho_registro=ARQUIVO_CONSULTAS,
    buscar=buscar_com_retentativa,
    agora=agora_utc,
):
    """Faz a consulta do dia, atualiza o cache e devolve a linha do registro e o código de saída.

    `validada_em` só anda com um 200 válido ou um 304 com lista em cache. Um 304 regrava
    a lista lida do cache, para o arquivo voltar a existir se tiver sumido no meio do caminho.
    """
    inicio = agora()
    cache = ler_cache(caminho_cache)
    tem_lista_anterior = cache["lista"] is not None

    resultado = buscar(etag_cache=cache["etag"])
    erro_tipo = resultado["erro_tipo"]
    erro_detalhe = resultado["erro_detalhe"]

    lista_a_gravar = None
    etag_a_gravar = None
    if resultado["lista"] is not None:
        # Menos da metade da lista anterior é mais provável ser erro do que mudança
        # real: mantém a anterior e registra (ADR-005).
        if tem_lista_anterior and 2 * len(resultado["lista"]) < len(cache["lista"]):
            erro_tipo = "ListaEncolheu"
            erro_detalhe = (
                f"{len(resultado['lista'])} organizações; "
                f"a lista anterior tem {len(cache['lista'])}"
            )
        else:
            lista_a_gravar = resultado["lista"]
            etag_a_gravar = resultado["etag"]
    elif resultado["status"] == 304:
        if tem_lista_anterior:
            lista_a_gravar = cache["lista"]
            etag_a_gravar = cache["etag"]
        else:
            erro_tipo = "304SemLista"
            erro_detalhe = "304 recebido sem lista em cache"

    gravou = False
    falhou_ao_gravar = False
    if lista_a_gravar is not None:
        try:
            gravar_cache(
                etag_a_gravar,
                lista_a_gravar,
                formatar_utc(inicio, timespec="seconds"),
                caminho_cache,
            )
            gravou = True
        except (OSError, RecursionError) as erro:
            # RecursionError: o json.dump aguenta menos aninhamento que o json.loads.
            falhou_ao_gravar = True
            erro_tipo = type(erro).__name__
            erro_detalhe = f"falha ao gravar o cache: {erro}"

    registro = {
        "timestamp_utc": formatar_utc(inicio),
        "status": resultado["status"],
        "etag": resultado["etag"],
        "last_modified": resultado["last_modified"],
        "organizacoes": resultado["organizacoes"],
        "tentativas": resultado["tentativas"],
        "usou_lista_anterior": tem_lista_anterior and not gravou,
        "erro_tipo": erro_tipo,
        "erro_detalhe": erro_detalhe,
        "problema_cache": cache["problema"],
    }

    codigo_saida = 0 if (gravou or tem_lista_anterior) and not falhou_ao_gravar else 1

    try:
        caminho_registro = Path(caminho_registro)
        caminho_registro.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n": no Windows o modo texto gravaria CRLF (dicionário: fim de linha LF)
        with caminho_registro.open("a", encoding="utf-8", newline="\n") as saida:
            saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError as erro:
        print(f"falha ao gravar o registro: {erro}", file=sys.stderr)
        codigo_saida = 1

    return registro, codigo_saida


def main():
    registro, codigo_saida = consultar_diretorio()
    print(
        f"{registro['timestamp_utc']} status={registro['status']} "
        f"organizacoes={registro['organizacoes']} tentativas={registro['tentativas']} "
        f"usou_lista_anterior={registro['usou_lista_anterior']} erro={registro['erro_tipo']}"
    )
    return codigo_saida


if __name__ == "__main__":
    sys.exit(main())
