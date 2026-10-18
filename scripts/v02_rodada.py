"""V-02: uma rodada de uma origem, com uma requisição GET por URL distinta da rota.

Uso:
    python scripts/v02_rodada.py --origem 1

Desenho e regras: docs/validacoes/V-02_bloqueio-ip-estrangeiro.md
Sem retentativa, sem paralelismo e sem guardar o corpo das respostas.
"""

import argparse
import hashlib
import json
import ssl
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import certifi
import requests

DIRETORIO_URL = "https://data.directory.openbankingbrasil.org.br/participants"
ROTA = "personal-loans"
TIMEOUT_S = 15  # página "Referência" da wiki do Open Finance, v26 (V-03, parte 3)
TIMEOUT_DIRETORIO_S = 60  # a lista tem cerca de 4,5 MB
PAUSA_S = 1
USER_AGENT = (
    "monitor-open-finance/0.1 "
    "(+https://github.com/liliamkezia-star/monitor-open-finance)"
)
PASTA_SAIDA = (
    Path(__file__).resolve().parent.parent
    / "docs" / "validacoes" / "evidencias" / "V-02"
)
# Raiz ICP-Brasil v10, que não está na lista da Mozilla (certifi). Baixada em 2026-10-18 de
# https://acraiz.icpbrasil.gov.br/credenciadas/RAIZ/ICP-Brasilv10.crt
RAIZ_ICP = Path(__file__).resolve().parent / "certificados" / "icp-brasil-raiz-v10.crt"
# SHA-256 do certificado em DER (não do arquivo, para não depender do fim de linha)
RAIZ_ICP_SHA256 = "6e0bff069a26994c15de2c4888cc54af84882e5495b7fbf66be9ccffec7489f6"


def agora_utc():
    return datetime.now(timezone.utc)


def montar_cadeia_confianca(pasta):
    """Junta as raízes do certifi com a raiz ICP-Brasil, depois de conferir o hash dela."""
    pem_icp = RAIZ_ICP.read_text(encoding="ascii")
    hash_icp = hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem_icp)).hexdigest()
    if hash_icp != RAIZ_ICP_SHA256:
        sys.exit(f"SHA-256 da raiz ICP-Brasil não confere ({hash_icp}). Nada foi medido.")
    caminho = Path(pasta) / "cadeia.pem"
    caminho.write_text(
        Path(certifi.where()).read_text(encoding="ascii") + "\n" + pem_icp,
        encoding="ascii",
    )
    return caminho


def baixar_diretorio(sessao):
    """Baixa a lista de participantes uma vez. Falha aqui encerra a rodada."""
    resposta = sessao.get(DIRETORIO_URL, timeout=TIMEOUT_DIRETORIO_S)
    resposta.raise_for_status()
    return resposta.json(), resposta.headers.get("Last-Modified")


def extrair_alvos(participantes, rota):
    """Devolve um alvo por URL distinta da rota, só de organizações e recursos ativos."""
    alvos = {}
    for org in participantes:
        if org.get("Status") != "Active":
            continue
        for servidor in org.get("AuthorisationServers") or []:
            for recurso in servidor.get("ApiResources") or []:
                if recurso.get("Status") != "Active":
                    continue
                for endpoint in recurso.get("ApiDiscoveryEndpoints") or []:
                    url = endpoint.get("ApiEndpoint", "").rstrip("/")
                    if url.endswith("/" + rota) and url not in alvos:
                        alvos[url] = {
                            "instituicao_id": org["OrganisationId"],
                            "instituicao_nome": org.get("OrganisationName"),
                            "url": url,
                            "versao_api": recurso.get("ApiVersion"),
                        }
    # ordem estável, para duas origens seguirem a mesma sequência
    return sorted(alvos.values(), key=lambda alvo: alvo["url"])


def corpo_e_json(resposta):
    try:
        resposta.json()
    except ValueError:
        return False
    return True


def medir(sessao, alvo, origem):
    """Faz uma requisição e devolve o registro. Erro inesperado sobe e para a rodada."""
    registro = {
        "timestamp_utc": agora_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "origem": origem,
        **alvo,
        "rota": "/" + ROTA,
        "categoria": None,
        "status": None,
        "erro_tipo": None,
        "erro_detalhe": None,
    }
    try:
        resposta = sessao.get(alvo["url"], timeout=TIMEOUT_S)
    # Timeout antes de ConnectionError: ConnectTimeout é subclasse das duas
    except requests.exceptions.Timeout as erro:
        registro["categoria"] = "timeout"
        registro["erro_tipo"] = type(erro).__name__
        registro["erro_detalhe"] = str(erro)[:300]
        return registro
    # inclui SSLError, conexão recusada, conexão resetada e falha de DNS
    except requests.exceptions.ConnectionError as erro:
        registro["categoria"] = "falha_conexao"
        registro["erro_tipo"] = type(erro).__name__
        registro["erro_detalhe"] = str(erro)[:300]
        return registro

    registro["status"] = resposta.status_code
    if resposta.status_code >= 500:
        registro["categoria"] = "5xx"
    elif resposta.status_code >= 400:
        registro["categoria"] = "4xx"
    elif corpo_e_json(resposta):
        registro["categoria"] = "sucesso"
    else:
        registro["categoria"] = "corpo_invalido"
    return registro


def sha256_arquivo(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--origem", type=int, choices=[1, 2, 3], required=True,
                        help="1 = residencial no Brasil, 2 = nuvem no Brasil, 3 = exterior")
    args = parser.parse_args()

    inicio = agora_utc()
    caminho = PASTA_SAIDA / f"{inicio:%Y-%m-%dT%H%MZ}_origem{args.origem}.jsonl"
    if caminho.exists():
        sys.exit(f"Já existe {caminho.name}. Espere o próximo minuto; nada foi sobrescrito.")
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    categorias = Counter()
    with tempfile.TemporaryDirectory() as pasta_temporaria:
        sessao = requests.Session()
        sessao.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        sessao.verify = str(montar_cadeia_confianca(pasta_temporaria))

        participantes, ultima_mudanca = baixar_diretorio(sessao)
        alvos = extrair_alvos(participantes, ROTA)
        print(f"Diretório: {len(participantes)} organizações (Last-Modified: {ultima_mudanca})")
        print(f"Rota /{ROTA}: {len(alvos)} URLs distintas de "
              f"{len({a['instituicao_id'] for a in alvos})} organizações")

        # "x": cria o arquivo e falha se ele já existir
        with caminho.open("x", encoding="utf-8", newline="\n") as saida:
            for i, alvo in enumerate(alvos, start=1):
                registro = medir(sessao, alvo, args.origem)
                saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
                saida.flush()
                categorias[registro["categoria"]] += 1
                print(f"[{i}/{len(alvos)}] {registro['categoria']:<14} {alvo['url']}")
                if i < len(alvos):
                    time.sleep(PAUSA_S)
        sessao.close()

    print()
    for categoria, total in categorias.most_common():
        print(f"{categoria:<14} {total}")
    print(f"\nArquivo: {caminho}")
    print(f"SHA-256: {sha256_arquivo(caminho)}")


if __name__ == "__main__":
    main()
