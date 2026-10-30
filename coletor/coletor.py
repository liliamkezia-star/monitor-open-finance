"""Coletor v1 (M1, bloco A1.4): mede uma vez um endpoint e grava um registro.

Uso:
    python coletor/coletor.py --origem 1

Formato do registro: docs/dicionario-de-dados.md (seção 1).
Prazo e fases: ADR-003. Ciclos de 15 min em UTC: ADR-002.
Sem retentativa e sem guardar o corpo da resposta.
"""

import argparse
import hashlib
import json
import re
import socket
import ssl
import subprocess
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import certifi

ESQUEMA_VERSAO = 1
COLETOR_VERSAO = "0.1.0"
PRAZO_S = 15  # prazo total de relógio, do DNS ao último byte (ADR-003, decisão 1)
USER_AGENT = (
    "monitor-open-finance/0.1 "
    "(+https://github.com/liliamkezia-star/monitor-open-finance)"
)
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")  # no Windows, precisa do pacote tzdata

RAIZ_REPO = Path(__file__).resolve().parent.parent
PASTA_SAIDA = RAIZ_REPO / "data" / "medicoes"
# Raiz ICP-Brasil v10, que não está no certifi (V-02). Mesma conferência da V-02:
# SHA-256 do certificado em DER, não do arquivo, para não depender do fim de linha.
RAIZ_ICP = RAIZ_REPO / "scripts" / "certificados" / "icp-brasil-raiz-v10.crt"
RAIZ_ICP_SHA256 = "6e0bff069a26994c15de2c4888cc54af84882e5495b7fbf66be9ccffec7489f6"

# v1: um endpoint fixo, que deu sucesso nas duas rodadas da V-02.
# A lista vinda do Diretório entra no A2.1.
ALVO = {
    "instituicao_id": "9294c0e8-ab01-5614-942d-97f261fe3454",
    "instituicao_nome": "CREFISA S.A. CFI",
    "familia": "opendata-loans",
    "rota": "/personal-loans",
    "url": "https://acp.crefisa.com.br/open-banking/opendata-loans/v1/personal-loans",
    "versao_api": "1.1.0",
}


class RespostaMalformada(Exception):
    """Chegaram bytes, mas não formam uma resposta HTTP válida."""


class CorpoInvalido(Exception):
    """O corpo não bate com o que os cabeçalhos declaram (truncado ou chunked quebrado)."""


def resolver_dns(host, porta, prazo_s):
    """Resolve o nome numa thread, esperando no máximo prazo_s.

    O getaddrinfo() ignora o settimeout do socket. A thread é daemon para o script
    não ficar preso esperando por ela ao terminar (ADR-002: sem sobreposição).
    """
    resultado = {}

    def tarefa():
        try:
            # Ponto 8 do dicionário: só IPv4 e só o primeiro endereço, para medir sempre
            # o mesmo caminho, sem a troca silenciosa de IP que um cliente comum faria.
            infos = socket.getaddrinfo(host, porta, socket.AF_INET, socket.SOCK_STREAM)
            resultado["endereco"] = infos[0][4]
        # largo de propósito: aqui só repassamos o erro; quem trata é a thread principal
        except Exception as erro:
            resultado["erro"] = erro

    thread = threading.Thread(target=tarefa, daemon=True)
    thread.start()
    thread.join(timeout=prazo_s)
    if thread.is_alive():
        raise TimeoutError(f"DNS não respondeu em {prazo_s:.2f} s")
    if "erro" in resultado:
        raise resultado["erro"]
    return resultado["endereco"]


def criar_contexto_tls(caminho_icp, hash_esperado):
    """Confia só no certifi e na raiz ICP-Brasil, nunca nas raízes do sistema."""
    pem_icp = Path(caminho_icp).read_text(encoding="ascii")
    hash_icp = hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem_icp)).hexdigest()
    if hash_icp != hash_esperado:
        raise ValueError(f"SHA-256 da raiz ICP-Brasil não confere ({hash_icp})")
    # PROTOCOL_TLS_CLIENT já exige certificado válido e confere o nome do host
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cafile=certifi.where())
    ctx.load_verify_locations(cadata=pem_icp)
    return ctx


def ms(inicio, fim):
    return round((fim - inicio) * 1000, 2)


def medir_requisicao(url, ctx, prazo_s=PRAZO_S):
    """Faz um GET e devolve (bytes da resposta ou None, resultado da rede).

    Falha de rede vira categoria timeout ou falha_conexao, com a fase.
    Quem olha status e corpo é montar_registro().
    """
    partes = urllib.parse.urlsplit(url)
    host = partes.hostname
    porta = partes.port or 443
    host_cabecalho = host if porta == 443 else f"{host}:{porta}"
    caminho = partes.path or "/"
    if partes.query:
        caminho += "?" + partes.query
    pedido = (
        f"GET {caminho} HTTP/1.1\r\n"
        f"Host: {host_cabecalho}\r\n"
        f"User-Agent: {USER_AGENT}\r\n"
        "Accept: application/json\r\n"
        "Accept-Encoding: identity\r\n"  # ponto 9: corpo sem compressão
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")

    resultado = {
        "inicio_utc": None,
        "categoria": None,
        "fase_falha": None,
        "erro_tipo": None,
        "erro_detalhe": None,
        "tempo_total_ms": None,
        "tempo_decorrido_ms": None,
        "tempo_dns_ms": None,
        "tempo_tcp_ms": None,
        "tempo_tls_ms": None,
        "tempo_primeiro_byte_ms": None,
        "tempo_download_ms": None,
    }
    resposta = None
    fase = "dns"

    # IN 615, 5.3.2, V: o horário é o de antes da requisição
    resultado["inicio_utc"] = datetime.now(timezone.utc)
    t_inicio = time.perf_counter()

    def restante():
        """Tempo que sobra do prazo total. Zero ou menos é timeout na fase atual."""
        sobra = prazo_s - (time.perf_counter() - t_inicio)
        if sobra <= 0:
            raise TimeoutError(f"prazo de {prazo_s} s esgotado")
        return sobra

    try:
        endereco = resolver_dns(host, porta, restante())
        resultado["tempo_dns_ms"] = ms(t_inicio, time.perf_counter())
        # o join e o settimeout podem passar um pouco do limite: conferir o prazo
        # ao fim de cada fase, para o estouro ser atribuído à fase em que aconteceu
        restante()

        fase = "tcp"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(restante())
            t0 = time.perf_counter()
            sock.connect(endereco)
            resultado["tempo_tcp_ms"] = ms(t0, time.perf_counter())
            restante()

            fase = "tls"
            sock.settimeout(restante())
            t0 = time.perf_counter()
            with ctx.wrap_socket(sock, server_hostname=host) as sock_tls:
                resultado["tempo_tls_ms"] = ms(t0, time.perf_counter())
                restante()

                fase = "primeiro_byte"
                sock_tls.settimeout(restante())
                sock_tls.sendall(pedido)
                t_envio = time.perf_counter()

                pedacos = []
                t_primeiro = t_ultimo = None
                while True:
                    # settimeout vale por recv, não pela fase: recalcular a cada volta
                    sock_tls.settimeout(restante())
                    pedaco = sock_tls.recv(65536)
                    if not pedaco:  # b'': o servidor fechou a conexão
                        break
                    t_ultimo = time.perf_counter()
                    if t_primeiro is None:
                        t_primeiro = t_ultimo
                        fase = "download"
                    pedacos.append(pedaco)

        if t_primeiro is None:
            raise ConnectionError("servidor fechou a conexão sem enviar dados")
        resultado["tempo_primeiro_byte_ms"] = ms(t_envio, t_primeiro)
        # até o último byte com dados, não até o b'' (IN 615, 5.3.2, V)
        resultado["tempo_download_ms"] = ms(t_primeiro, t_ultimo)
        resultado["tempo_total_ms"] = ms(t_inicio, t_ultimo)
        resposta = b"".join(pedacos)

    # TimeoutError antes de OSError: TimeoutError é subclasse de OSError
    except TimeoutError as erro:
        resultado["categoria"] = "timeout"
        resultado["fase_falha"] = fase
        resultado["erro_tipo"] = type(erro).__name__
        resultado["erro_detalhe"] = str(erro)[:300]
    # inclui falha de DNS (gaierror), conexão recusada, SSLError e resposta vazia
    except OSError as erro:
        resultado["categoria"] = "falha_conexao"
        resultado["fase_falha"] = fase
        resultado["erro_tipo"] = type(erro).__name__
        resultado["erro_detalhe"] = str(erro)[:300]

    # sempre preenchido, inclusive em falha, para auditar o prazo (ADR-003)
    resultado["tempo_decorrido_ms"] = ms(t_inicio, time.perf_counter())
    return resposta, resultado


def separar_resposta(bytes_crus):
    """Devolve (status, cabeçalhos com nome em minúsculas, corpo ainda cru)."""
    fim = bytes_crus.find(b"\r\n\r\n")
    if fim == -1:
        raise RespostaMalformada("separador de cabeçalho ausente")
    linhas = bytes_crus[:fim].split(b"\r\n")
    corpo = bytes_crus[fim + 4:]

    partes = linhas[0].split(b" ", 2)
    if not partes[0].startswith(b"HTTP/1.") or len(partes) < 2:
        raise RespostaMalformada("primeira linha não é HTTP/1.x")
    if not (len(partes[1]) == 3 and partes[1].isdigit()):
        raise RespostaMalformada("código de status inválido")
    status = int(partes[1])
    if not 100 <= status <= 599:
        raise RespostaMalformada(f"status fora da faixa HTTP: {status}")

    cabecalhos = {}
    for linha in linhas[1:]:
        nome, separador, valor = linha.partition(b":")
        if separador:
            # latin-1 decodifica qualquer byte; ascii com errors='ignore' apagaria bytes
            cabecalhos[nome.strip().lower().decode("latin-1")] = valor.strip().decode("latin-1")
    return status, cabecalhos, corpo


def decodificar_chunked(corpo):
    """Junta os pedaços de um corpo chunked. Corpo incompleto lança CorpoInvalido."""
    saida = bytearray()
    posicao = 0
    while True:
        fim_linha = corpo.find(b"\r\n", posicao)
        if fim_linha == -1:
            raise CorpoInvalido("chunked sem o pedaço final de tamanho 0")
        # extensões depois de ';' são ignoradas (RFC 9112, 7.1.1)
        tamanho_hex = corpo[posicao:fim_linha].split(b";")[0].strip()
        try:
            tamanho = int(tamanho_hex, 16)
        except ValueError:
            raise CorpoInvalido(f"tamanho de pedaço inválido: {tamanho_hex[:20]!r}") from None
        if tamanho == 0:
            return bytes(saida)
        inicio = fim_linha + 2
        fim = inicio + tamanho
        if corpo[fim:fim + 2] != b"\r\n":
            raise CorpoInvalido("pedaço truncado ou sem CRLF no fim")
        saida += corpo[inicio:fim]
        posicao = fim + 2


def extrair_corpo(cabecalhos, corpo_cru):
    """Devolve o corpo de verdade, conferido contra o que os cabeçalhos declaram."""
    codificacao = cabecalhos.get("transfer-encoding", "").lower()
    # chunked vence o Content-Length quando os dois vêm (RFC 9112, 6.3)
    if codificacao.split(",")[-1].strip() == "chunked":
        return decodificar_chunked(corpo_cru)
    declarado = cabecalhos.get("content-length")
    if declarado is not None:
        if not declarado.isdigit():
            raise CorpoInvalido(f"Content-Length inválido: {declarado[:20]!r}")
        if len(corpo_cru) != int(declarado):
            raise CorpoInvalido(
                f"corpo com {len(corpo_cru)} bytes, Content-Length declara {declarado}"
            )
    return corpo_cru


def categoria_do_status(status):
    """Só para status fora de 2xx. 2xx depende do corpo (dicionário, ponto 7)."""
    if status >= 500:
        return "5xx"
    if status >= 400:
        return "4xx"
    if status >= 300:
        return "3xx"
    # 1xx não deveria chegar aqui sozinho: tratado como resposta malformada
    raise RespostaMalformada(f"resposta final com status {status}")


def e_json(corpo):
    try:
        json.loads(corpo)
    # JSONDecodeError e UnicodeDecodeError são subclasses de ValueError
    except ValueError:
        return False
    return True


def formatar_utc(instante, timespec="milliseconds"):
    return instante.isoformat(timespec=timespec).replace("+00:00", "Z")


def ciclo_de(instante):
    """Início do bloco de 15 min, na grade fixa em UTC, que contém o instante (ADR-002)."""
    return instante.replace(minute=instante.minute - instante.minute % 15,
                            second=0, microsecond=0)


def versao_major_de(url):
    achado = re.search(r"/v(\d+)/", url)
    if achado is None:
        raise ValueError(f"URL sem /vN/ no caminho: {url}")  # ponto 4 do dicionário
    return int(achado.group(1))


def versao_do_coletor():
    """Versão + commit curto, para separar séries se o método mudar."""
    try:
        saida = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=RAIZ_REPO, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return COLETOR_VERSAO
    if saida.returncode != 0:
        return COLETOR_VERSAO
    return f"{COLETOR_VERSAO}+{saida.stdout.strip()}"


def montar_registro(alvo, origem, resposta, rede, coletor_versao):
    """Monta o registro completo, na ordem do dicionário de dados (seção 1)."""
    inicio = rede["inicio_utc"]
    registro = {
        # 1.1 Quando e de onde
        "esquema_versao": ESQUEMA_VERSAO,
        "ciclo_utc": formatar_utc(ciclo_de(inicio), timespec="seconds"),
        "timestamp_utc": formatar_utc(inicio),
        "timestamp_brasilia": inicio.astimezone(FUSO_BRASILIA).isoformat(timespec="milliseconds"),
        "origem": origem,
        "coletor_versao": coletor_versao,
        # 1.2 O que foi medido
        "instituicao_id": alvo["instituicao_id"],
        "instituicao_nome": alvo["instituicao_nome"],
        "familia": alvo["familia"],
        "rota": alvo["rota"],
        "url": alvo["url"],
        "versao_api": alvo["versao_api"],
        "versao_major": versao_major_de(alvo["url"]),
        "diretorio_etag": None,  # o Diretório entra no A2.1
        # 1.3 Resultado
        "categoria": rede["categoria"],
        "status": None,
        "fase_falha": rede["fase_falha"],
        "erro_tipo": rede["erro_tipo"],
        "erro_detalhe": rede["erro_detalhe"],
        # 1.4 Tempos
        "tempo_total_ms": rede["tempo_total_ms"],
        "tempo_decorrido_ms": rede["tempo_decorrido_ms"],
        "tempo_dns_ms": rede["tempo_dns_ms"],
        "tempo_tcp_ms": rede["tempo_tcp_ms"],
        "tempo_tls_ms": rede["tempo_tls_ms"],
        "tempo_primeiro_byte_ms": rede["tempo_primeiro_byte_ms"],
        "tempo_download_ms": rede["tempo_download_ms"],
        # 1.5 Corpo da resposta
        "corpo_bytes": None,
        "corpo_sha256": None,
        "content_type": None,
    }
    if resposta is None:  # falhou na rede; a categoria já veio de medir_requisicao
        return registro

    try:
        status, cabecalhos, corpo_cru = separar_resposta(resposta)
        categoria = None if 200 <= status < 300 else categoria_do_status(status)
    except RespostaMalformada as erro:
        # ponto 10: sem status não há 4xx/5xx; os bytes chegaram, mas não serviram
        registro.update({
            "categoria": "falha_conexao",
            "fase_falha": "download",
            "erro_tipo": type(erro).__name__,
            "erro_detalhe": str(erro)[:300],
            "tempo_total_ms": None,  # não houve resposta válida
        })
        return registro

    registro["status"] = status
    registro["content_type"] = cabecalhos.get("content-type")
    try:
        corpo = extrair_corpo(cabecalhos, corpo_cru)
    except CorpoInvalido as erro:
        # 2xx com corpo quebrado é corpo_invalido; 3xx/4xx/5xx continuam como estão
        registro["categoria"] = categoria or "corpo_invalido"
        registro["erro_tipo"] = type(erro).__name__
        registro["erro_detalhe"] = str(erro)[:300]
        return registro

    registro["corpo_bytes"] = len(corpo)
    registro["corpo_sha256"] = hashlib.sha256(corpo).hexdigest()
    if categoria is None:
        categoria = "sucesso" if e_json(corpo) else "corpo_invalido"
    registro["categoria"] = categoria
    return registro


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--origem", type=int, choices=[1, 2, 3], required=True,
                        help="1 = residencial no Brasil, 2 = nuvem no Brasil, 3 = exterior")
    parser.add_argument("--prazo", type=float, default=PRAZO_S,
                        help="prazo total em segundos (só para testar o timeout à mão)")
    args = parser.parse_args()

    # fora do relógio da medição: carregar as raízes leva alguns milissegundos
    ctx = criar_contexto_tls(RAIZ_ICP, RAIZ_ICP_SHA256)
    coletor_versao = versao_do_coletor()

    resposta, rede = medir_requisicao(ALVO["url"], ctx, args.prazo)
    registro = montar_registro(ALVO, args.origem, resposta, rede, coletor_versao)

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_SAIDA / f"{registro['ciclo_utc'][:10]}.jsonl"  # um arquivo por dia UTC
    # newline="\n": no Windows o modo texto gravaria CRLF (dicionário: fim de linha LF)
    with caminho.open("a", encoding="utf-8", newline="\n") as saida:
        saida.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"{registro['timestamp_utc']} {registro['categoria']:<14} "
          f"status={registro['status']} total_ms={registro['tempo_total_ms']} -> {caminho}")


if __name__ == "__main__":
    main()
