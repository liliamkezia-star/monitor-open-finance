import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import requests

from coletor import diretorio
from coletor.coletor import USER_AGENT

LISTA = [{"OrganisationId": "a"}]
LISTA_NOVA = [{"OrganisationId": "a"}, {"OrganisationId": "b"}]
VALIDADA_EM = "2026-11-01T12:00:00Z"


def resposta_http(status=200, corpo=b"", cabecalhos=None):
    """Uma Response de verdade, para .content e .headers serem os do requests."""
    resposta = requests.Response()
    resposta.status_code = status
    resposta._content = corpo
    resposta.headers.update(cabecalhos or {})
    return resposta


class TestMotivoListaInvalida(unittest.TestCase):

    def test_caminho_feliz(self):
        # Uma lista válida com OrganisationId explícito deve retornar None
        entrada = [{"OrganisationId": "A1"}, {"OrganisationId": "B2"}]
        self.assertIsNone(diretorio.motivo_lista_invalida(entrada))

    def test_raiz_invalida(self):
        # "raiz" só aparece nesta mensagem: "lista" também casaria com "lista vazia"
        casos = [None, {"OrganisationId": "A1"}, "string"]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                motivo = diretorio.motivo_lista_invalida(entrada)
                self.assertIsNotNone(motivo)
                self.assertRegex(motivo.lower(), "raiz")

    def test_lista_vazia(self):
        # Formato correto (lista), mas quebra a premissa de negócio
        motivo = diretorio.motivo_lista_invalida([])
        self.assertIsNotNone(motivo)
        self.assertRegex(motivo.lower(), "vazia")

    def test_itens_tipo_errado(self):
        # A lista existe, mas um item não é objeto; o índice aponta qual
        casos = [
            ([1, 2], "item 0"),
            (["A1", "B2"], "item 0"),
            ([{"OrganisationId": "A1"}, "string_no_meio"], "item 1"),
        ]
        for entrada, item_esperado in casos:
            with self.subTest(entrada=entrada):
                motivo = diretorio.motivo_lista_invalida(entrada)
                self.assertIsNotNone(motivo)
                self.assertRegex(motivo, item_esperado)
                self.assertRegex(motivo.lower(), "não é objeto")

    def test_organisation_id_ausente_ou_invalido(self):
        # Erros na principal chave exigida pelo ADR-004
        casos = [
            ([{"OrganisationName": "x"}], "ausente"),
            ([{"OrganisationId": ""}], "vazio"),
            ([{"OrganisationId": None}], "nulo"),
            ([{"OrganisationId": 5}], "não é texto"),
        ]
        for entrada, erro_logico in casos:
            with self.subTest(erro_logico=erro_logico, entrada=entrada):
                motivo = diretorio.motivo_lista_invalida(entrada)
                self.assertIsNotNone(motivo)
                self.assertRegex(motivo, "item 0")
                self.assertRegex(motivo.lower(), "organisationid")

    def test_item_invalido_no_final(self):
        # Prova que a varredura não checa apenas o dados[0]
        entrada = [{"OrganisationId": "A1"}, {"x": 1}]
        motivo = diretorio.motivo_lista_invalida(entrada)

        self.assertIsNotNone(motivo)
        # Ao buscar por 'item 1', garantimos que o laço leu até o segundo elemento
        self.assertRegex(motivo.lower(), "item 1")


class TestFazerUmaTentativa(unittest.TestCase):

    def setUp(self):
        patcher = patch.object(diretorio.requests, "get")
        self.get = patcher.start()
        self.addCleanup(patcher.stop)

    def test_200_valido(self):
        self.get.return_value = resposta_http(
            200,
            json.dumps(LISTA).encode(),
            {"ETag": '"e"', "Last-Modified": "ontem"},
        )
        resultado = diretorio.fazer_uma_tentativa("http://x")
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["etag"], '"e"')
        self.assertEqual(resultado["last_modified"], "ontem")
        self.assertEqual(resultado["lista"], LISTA)
        self.assertEqual(resultado["organizacoes"], 1)
        self.assertIsNone(resultado["erro_tipo"])
        self.assertFalse(resultado["deve_retentar"])

    def test_pedido_leva_user_agent_e_timeout_de_60(self):
        self.get.return_value = resposta_http(304)
        diretorio.fazer_uma_tentativa("http://x")
        argumentos = self.get.call_args
        self.assertEqual(argumentos.args, ("http://x",))
        self.assertEqual(argumentos.kwargs["timeout"], 60)  # ADR-003, decisão 5
        self.assertEqual(argumentos.kwargs["headers"]["User-Agent"], USER_AGENT)

    def test_if_none_match_so_com_etag(self):
        self.get.return_value = resposta_http(304)
        diretorio.fazer_uma_tentativa("http://x", '"e"')
        self.assertEqual(self.get.call_args.kwargs["headers"]["If-None-Match"], '"e"')
        diretorio.fazer_uma_tentativa("http://x")
        self.assertNotIn("If-None-Match", self.get.call_args.kwargs["headers"])

    def test_304_nao_e_erro_e_nao_traz_lista(self):
        self.get.return_value = resposta_http(304, b"", {"ETag": '"e"'})
        resultado = diretorio.fazer_uma_tentativa("http://x", '"e"')
        self.assertEqual(resultado["status"], 304)
        self.assertIsNone(resultado["lista"])
        self.assertIsNone(resultado["erro_tipo"])
        self.assertFalse(resultado["deve_retentar"])

    def test_status_inesperado(self):
        casos = [
            (500, True),
            (503, True),
            (599, True),
            (204, False),
            (301, False),
            (400, False),
            (404, False),
            (429, False),  # ADR-002: 429 nunca é motivo para retentar
            (499, False),
        ]
        for status, retenta in casos:
            with self.subTest(status=status):
                self.get.return_value = resposta_http(status)
                resultado = diretorio.fazer_uma_tentativa("http://x")
                self.assertEqual(resultado["status"], status)
                self.assertEqual(resultado["erro_tipo"], "StatusInesperado")
                self.assertEqual(resultado["deve_retentar"], retenta)
                self.assertIsNone(resultado["lista"])

    def test_200_que_nao_e_json(self):
        casos = [b"", b"<html>", b"[" * 200000]  # o último dá RecursionError
        for corpo in casos:
            with self.subTest(corpo=corpo[:10]):
                self.get.return_value = resposta_http(200, corpo)
                resultado = diretorio.fazer_uma_tentativa("http://x")
                self.assertIsNotNone(resultado["erro_tipo"])
                self.assertIsNone(resultado["lista"])
                self.assertFalse(resultado["deve_retentar"])

    def test_200_fora_de_utf8_e_recusado(self):
        # O .json() do requests tentaria adivinhar a codificação e corromperia o texto.
        self.get.return_value = resposta_http(200, b'[{"OrganisationId": "\xe9"}]')
        resultado = diretorio.fazer_uma_tentativa("http://x")
        self.assertEqual(resultado["erro_tipo"], "UnicodeDecodeError")
        self.assertIsNone(resultado["lista"])
        self.assertFalse(resultado["deve_retentar"])

    def test_200_em_utf8_com_acento_e_bom(self):
        casos = {
            "acento": '[{"OrganisationId": "CRÉDITO"}]'.encode("utf-8"),
            "bom": '﻿[{"OrganisationId": "CRÉDITO"}]'.encode("utf-8"),
        }
        for nome, corpo in casos.items():
            with self.subTest(caso=nome):
                self.get.return_value = resposta_http(200, corpo)
                resultado = diretorio.fazer_uma_tentativa("http://x")
                self.assertEqual(resultado["lista"], [{"OrganisationId": "CRÉDITO"}])

    def test_200_com_lista_invalida(self):
        for corpo in [b"[]", b"null", b'{"message": "m"}', b"[1, 2]"]:
            with self.subTest(corpo=corpo):
                self.get.return_value = resposta_http(200, corpo, {"ETag": '"ruim"'})
                resultado = diretorio.fazer_uma_tentativa("http://x")
                self.assertEqual(resultado["erro_tipo"], "ListaInvalida")
                self.assertIsNone(resultado["lista"])
                self.assertIsNone(resultado["organizacoes"])
                self.assertFalse(resultado["deve_retentar"])

    def test_falhas_de_rede_retentam(self):
        casos = [
            requests.exceptions.ConnectTimeout("t"),
            requests.exceptions.ReadTimeout("t"),
            requests.exceptions.ConnectionError("c"),
            requests.exceptions.SSLError("s"),
            requests.exceptions.ChunkedEncodingError("corpo truncado"),
        ]
        for erro in casos:
            with self.subTest(erro=type(erro).__name__):
                self.get.side_effect = erro
                resultado = diretorio.fazer_uma_tentativa("http://x")
                self.assertIsNone(resultado["status"])
                self.assertEqual(resultado["erro_tipo"], type(erro).__name__)
                self.assertTrue(resultado["deve_retentar"])

    def test_outro_erro_do_requests_nao_retenta(self):
        self.get.side_effect = requests.exceptions.TooManyRedirects("r")
        resultado = diretorio.fazer_uma_tentativa("http://x")
        self.assertEqual(resultado["erro_tipo"], "TooManyRedirects")
        self.assertFalse(resultado["deve_retentar"])

    def test_erro_de_programacao_nao_e_escondido(self):
        # Um except largo faria um bug parecer uma queda do Diretório.
        self.get.side_effect = KeyError("bug")
        with self.assertRaises(KeyError):
            diretorio.fazer_uma_tentativa("http://x")


class TestBuscarComRetentativa(unittest.TestCase):

    FALHA = {"status": 503, "deve_retentar": True}
    SUCESSO = {"status": 200, "deve_retentar": False}
    DEFINITIVA = {"status": 404, "deve_retentar": False}

    def buscar(self, respostas, **argumentos):
        """Devolve o resultado, as chamadas ao fetcher e as pausas pedidas."""
        fila = [dict(resposta) for resposta in respostas]
        chamadas = []
        pausas = []

        def fetcher(url, etag):
            chamadas.append((url, etag))
            return fila.pop(0)

        resultado = diretorio.buscar_com_retentativa(
            "http://x", '"e"', fetcher=fetcher, sleeper=pausas.append, **argumentos
        )
        return resultado, chamadas, pausas

    def test_primeira_da_certo(self):
        resultado, chamadas, pausas = self.buscar([self.SUCESSO])
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["tentativas"], 1)
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(pausas, [])

    def test_erro_definitivo_nao_retenta(self):
        resultado, chamadas, pausas = self.buscar([self.DEFINITIVA])
        self.assertEqual(resultado["status"], 404)
        self.assertEqual(resultado["tentativas"], 1)
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(pausas, [])

    def test_segunda_da_certo(self):
        resultado, chamadas, pausas = self.buscar([self.FALHA, self.SUCESSO])
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["tentativas"], 2)
        self.assertEqual(len(chamadas), 2)
        self.assertEqual(pausas, [5])

    def test_falha_definitiva_depois_de_transitoria_para(self):
        resultado, chamadas, pausas = self.buscar([self.FALHA, self.DEFINITIVA])
        self.assertEqual(resultado["status"], 404)
        self.assertEqual(len(chamadas), 2)
        self.assertEqual(pausas, [5])

    def test_tres_falhas_devolvem_a_ultima_sem_pausa_no_fim(self):
        ultima = {"status": 500, "deve_retentar": True}
        resultado, chamadas, pausas = self.buscar([self.FALHA, self.FALHA, ultima])
        self.assertEqual(resultado["status"], 500)
        self.assertEqual(resultado["tentativas"], 3)
        self.assertEqual(len(chamadas), 3)
        self.assertEqual(pausas, [5, 10])

    def test_pausas_definem_o_numero_de_tentativas(self):
        casos = [((), 1, []), ((7,), 2, [7]), ((1, 2, 3), 4, [1, 2, 3])]
        for valores, tentativas, esperadas in casos:
            with self.subTest(pausas=valores):
                respostas = [self.FALHA] * 5
                resultado, chamadas, pausas = self.buscar(respostas, pausas=valores)
                self.assertEqual(resultado["tentativas"], tentativas)
                self.assertEqual(len(chamadas), tentativas)
                self.assertEqual(pausas, esperadas)

    def test_toda_tentativa_usa_a_mesma_url_e_o_mesmo_etag(self):
        _, chamadas, _ = self.buscar([self.FALHA, self.SUCESSO])
        self.assertEqual(chamadas, [("http://x", '"e"'), ("http://x", '"e"')])

    def test_chave_escrita_errada_nao_passa_calada(self):
        with self.assertRaises(KeyError):
            self.buscar([{"status": 503, "deve_retenta": True}, self.SUCESSO])


class TestCache(unittest.TestCase):

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta = Path(pasta.name)
        self.cache = self.pasta / "sub" / "participantes.json"

    def arquivos_na_pasta(self):
        return sorted(item.name for item in self.cache.parent.iterdir())

    def test_sem_arquivo_nao_e_problema(self):
        self.assertEqual(
            diretorio.ler_cache(self.cache),
            {"etag": None, "validada_em": None, "lista": None, "problema": None},
        )

    def test_ida_e_volta(self):
        lista = [{"OrganisationId": "a", "OrganisationName": "CRÉDITO"}]
        diretorio.gravar_cache('"e"', lista, VALIDADA_EM, self.cache)
        self.assertEqual(
            diretorio.ler_cache(self.cache),
            {"etag": '"e"', "validada_em": VALIDADA_EM, "lista": lista, "problema": None},
        )

    def test_etag_nulo_e_valido(self):
        diretorio.gravar_cache(None, LISTA, VALIDADA_EM, self.cache)
        lido = diretorio.ler_cache(self.cache)
        self.assertIsNone(lido["etag"])
        self.assertEqual(lido["lista"], LISTA)
        self.assertIsNone(lido["problema"])

    def test_surrogate_solto_nao_quebra_a_gravacao(self):
        lista = [{"OrganisationId": "\ud800"}]
        diretorio.gravar_cache('"e"', lista, VALIDADA_EM, self.cache)
        self.assertEqual(diretorio.ler_cache(self.cache)["lista"], lista)

    def test_arquivo_ruim_nao_devolve_etag_nem_lista(self):
        boa = b'"lista": [{"OrganisationId": "a"}]'
        data = b'"validada_em": "' + VALIDADA_EM.encode() + b'"'
        casos = {
            "vazio": b"",
            "pela metade": b'{"etag": "x", "lista": [{"Organ',
            "binario": b"\xff\xfe\x00lixo",
            "aninhado": b"[" * 200000,
            "null": b"null",
            "raiz lista": b"[]",
            "sem lista": b'{"etag": "x", ' + data + b"}",
            "lista vazia": b'{"etag": "x", ' + data + b', "lista": []}',
            "item sem id": b'{"etag": "x", ' + data + b', "lista": [{"a": 1}]}',
            "etag numero": b'{"etag": 5, ' + data + b", " + boa + b"}",
            "sem data": b'{"etag": "x", ' + boa + b"}",
            "data numero": b'{"etag": "x", "validada_em": 5, ' + boa + b"}",
            "data ruim": b'{"etag": "x", "validada_em": "ontem", ' + boa + b"}",
            "data sem fuso": b'{"etag": "x", "validada_em": "2026-11-01T12:00:00", '
            + boa
            + b"}",
        }
        self.cache.parent.mkdir(parents=True)
        for nome, bruto in casos.items():
            with self.subTest(caso=nome):
                self.cache.write_bytes(bruto)
                lido = diretorio.ler_cache(self.cache)
                self.assertIsNone(lido["etag"])
                self.assertIsNone(lido["lista"])
                self.assertIsNone(lido["validada_em"])
                self.assertIsNotNone(lido["problema"])

    def test_gravar_cria_a_pasta_e_nao_deixa_temporario(self):
        diretorio.gravar_cache('"e"', LISTA, VALIDADA_EM, self.cache)
        self.assertEqual(self.arquivos_na_pasta(), ["participantes.json"])

    def test_temporario_na_mesma_pasta_e_fsync_antes_da_troca(self):
        eventos = []
        fsync_real = os.fsync
        replace_real = os.replace

        def fsync(descritor):
            eventos.append("fsync")
            fsync_real(descritor)

        def replace(origem, destino):
            eventos.append("replace")
            self.assertEqual(Path(origem).parent, Path(destino).parent)
            replace_real(origem, destino)

        with patch.object(diretorio.os, "fsync", fsync), patch.object(
            diretorio.os, "replace", replace
        ):
            diretorio.gravar_cache('"e"', LISTA, VALIDADA_EM, self.cache)
        self.assertEqual(eventos, ["fsync", "replace"])

    def test_falha_na_troca_preserva_o_cache_e_limpa_o_temporario(self):
        diretorio.gravar_cache('"velho"', LISTA, VALIDADA_EM, self.cache)
        with patch.object(diretorio.os, "replace", side_effect=PermissionError("uso")):
            with self.assertRaises(PermissionError):
                diretorio.gravar_cache('"novo"', LISTA_NOVA, VALIDADA_EM, self.cache)
        self.assertEqual(diretorio.ler_cache(self.cache)["etag"], '"velho"')
        self.assertEqual(self.arquivos_na_pasta(), ["participantes.json"])

    def test_lista_que_nao_vira_json_preserva_o_cache(self):
        diretorio.gravar_cache('"velho"', LISTA, VALIDADA_EM, self.cache)
        with self.assertRaises(TypeError):
            diretorio.gravar_cache('"novo"', [{"x": object()}], VALIDADA_EM, self.cache)
        self.assertEqual(diretorio.ler_cache(self.cache)["etag"], '"velho"')
        self.assertEqual(self.arquivos_na_pasta(), ["participantes.json"])


class TestConsultarDiretorio(unittest.TestCase):

    AGORA = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    AGORA_TEXTO = "2026-11-03T12:00:00Z"

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.cache = Path(pasta.name) / "participantes.json"
        self.registro = Path(pasta.name) / "consultas.jsonl"

    def resultado(self, status=None, etag=None, lista=None, erro=None, tentativas=1):
        return {
            "status": status,
            "etag": etag,
            "last_modified": None,
            "organizacoes": len(lista) if lista else None,
            "lista": lista,
            "erro_tipo": erro,
            "erro_detalhe": erro,
            "deve_retentar": False,
            "tentativas": tentativas,
        }

    def cache_anterior(self):
        diretorio.gravar_cache('"velho"', LISTA, VALIDADA_EM, self.cache)

    def rodar(self, resultado):
        self.etags_enviados = []

        def buscar(etag_cache=None):
            self.etags_enviados.append(etag_cache)
            return resultado

        return diretorio.consultar_diretorio(
            self.cache, self.registro, buscar, lambda: self.AGORA
        )

    def test_200_sem_cache(self):
        registro, codigo = self.rodar(self.resultado(200, '"novo"', LISTA_NOVA))
        self.assertEqual(codigo, 0)
        self.assertFalse(registro["usou_lista_anterior"])
        self.assertEqual(self.etags_enviados, [None])
        lido = diretorio.ler_cache(self.cache)
        self.assertEqual(lido["etag"], '"novo"')
        self.assertEqual(lido["lista"], LISTA_NOVA)
        self.assertEqual(lido["validada_em"], self.AGORA_TEXTO)

    def test_200_substitui_a_lista_anterior(self):
        self.cache_anterior()
        registro, codigo = self.rodar(self.resultado(200, '"novo"', LISTA_NOVA))
        self.assertEqual(codigo, 0)
        self.assertFalse(registro["usou_lista_anterior"])
        self.assertEqual(self.etags_enviados, ['"velho"'])
        self.assertEqual(diretorio.ler_cache(self.cache)["lista"], LISTA_NOVA)

    def test_304_mantem_a_lista_e_atualiza_validada_em(self):
        self.cache_anterior()
        registro, codigo = self.rodar(self.resultado(304, '"velho"'))
        self.assertEqual(codigo, 0)
        self.assertFalse(registro["usou_lista_anterior"])
        self.assertIsNone(registro["erro_tipo"])
        lido = diretorio.ler_cache(self.cache)
        self.assertEqual(lido["lista"], LISTA)
        self.assertEqual(lido["etag"], '"velho"')
        self.assertEqual(lido["validada_em"], self.AGORA_TEXTO)

    def test_304_com_outro_etag_mantem_o_par_do_cache(self):
        self.cache_anterior()
        self.rodar(self.resultado(304, '"outro"'))
        self.assertEqual(diretorio.ler_cache(self.cache)["etag"], '"velho"')

    def test_304_sem_lista_e_falha(self):
        registro, codigo = self.rodar(self.resultado(304, '"x"'))
        self.assertEqual(codigo, 1)
        self.assertEqual(registro["erro_tipo"], "304SemLista")
        self.assertFalse(registro["usou_lista_anterior"])
        self.assertFalse(self.cache.exists())

    def test_falha_com_cache_mantem_tudo(self):
        self.cache_anterior()
        registro, codigo = self.rodar(self.resultado(503, '"x"', erro="StatusInesperado"))
        self.assertEqual(codigo, 0)
        self.assertTrue(registro["usou_lista_anterior"])
        self.assertEqual(registro["erro_tipo"], "StatusInesperado")
        lido = diretorio.ler_cache(self.cache)
        self.assertEqual(lido["etag"], '"velho"')
        self.assertEqual(lido["validada_em"], VALIDADA_EM)

    def test_falha_sem_cache_sai_com_1(self):
        registro, codigo = self.rodar(self.resultado(erro="ConnectionError"))
        self.assertEqual(codigo, 1)
        self.assertFalse(registro["usou_lista_anterior"])

    def test_etag_de_lista_invalida_nao_vai_para_o_cache(self):
        self.cache_anterior()
        registro, _ = self.rodar(self.resultado(200, '"ruim"', erro="ListaInvalida"))
        self.assertEqual(registro["etag"], '"ruim"')  # o registro guarda o que veio
        self.assertEqual(diretorio.ler_cache(self.cache)["etag"], '"velho"')

    def test_cache_corrompido_nao_envia_etag_e_e_recuperado(self):
        self.cache.write_bytes(b'{"etag": "velho"')
        registro, codigo = self.rodar(self.resultado(200, '"novo"', LISTA_NOVA))
        self.assertEqual(self.etags_enviados, [None])
        self.assertEqual(codigo, 0)
        self.assertIsNotNone(registro["problema_cache"])
        self.assertIsNone(diretorio.ler_cache(self.cache)["problema"])

    def test_cache_corrompido_e_falha_sai_com_1(self):
        self.cache.write_bytes(b'{"etag": "velho"')
        registro, codigo = self.rodar(self.resultado(503, erro="StatusInesperado"))
        self.assertEqual(codigo, 1)
        self.assertFalse(registro["usou_lista_anterior"])
        self.assertIsNotNone(registro["problema_cache"])

    def test_falha_ao_gravar_sai_com_1_e_e_registrada(self):
        casos = {
            "200": self.resultado(200, '"novo"', LISTA_NOVA),
            "304": self.resultado(304, '"velho"'),
        }
        for nome, resultado in casos.items():
            with self.subTest(caso=nome):
                self.cache_anterior()
                with patch.object(
                    diretorio.os, "replace", side_effect=PermissionError("uso")
                ):
                    registro, codigo = self.rodar(resultado)
                self.assertEqual(codigo, 1)
                self.assertEqual(registro["erro_tipo"], "PermissionError")
                self.assertTrue(registro["usou_lista_anterior"])
                self.assertEqual(diretorio.ler_cache(self.cache)["validada_em"], VALIDADA_EM)

    def test_json_fundo_demais_para_gravar_e_falha_registrada(self):
        # Passa no json.loads, mas o json.dump recursivo não aguenta.
        fundo = []
        for _ in range(sys.getrecursionlimit() + 100):
            fundo = [fundo]
        lista = [{"OrganisationId": "a", "x": fundo}]
        self.cache_anterior()
        registro, codigo = self.rodar(self.resultado(200, '"novo"', lista))
        self.assertEqual(codigo, 1)
        self.assertEqual(registro["erro_tipo"], "RecursionError")
        self.assertTrue(registro["usou_lista_anterior"])
        self.assertTrue(self.registro.exists())
        lido = diretorio.ler_cache(self.cache)
        self.assertEqual(lido["etag"], '"velho"')
        self.assertEqual(lido["validada_em"], VALIDADA_EM)

    def lista_de(self, tamanho):
        return [{"OrganisationId": str(numero)} for numero in range(tamanho)]

    def test_lista_com_menos_da_metade_e_recusada(self):
        casos = [(4, 1), (3, 1), (105, 1), (105, 52)]
        for anterior, nova in casos:
            with self.subTest(anterior=anterior, nova=nova):
                diretorio.gravar_cache(
                    '"velho"', self.lista_de(anterior), VALIDADA_EM, self.cache
                )
                registro, codigo = self.rodar(
                    self.resultado(200, '"novo"', self.lista_de(nova))
                )
                self.assertEqual(codigo, 0)  # há lista válida em cache
                self.assertEqual(registro["erro_tipo"], "ListaEncolheu")
                self.assertTrue(registro["usou_lista_anterior"])
                self.assertEqual(registro["organizacoes"], nova)
                lido = diretorio.ler_cache(self.cache)
                self.assertEqual(lido["etag"], '"velho"')
                self.assertEqual(len(lido["lista"]), anterior)
                self.assertEqual(lido["validada_em"], VALIDADA_EM)

    def test_lista_com_a_metade_ou_mais_e_aceita(self):
        casos = [(4, 2), (3, 2), (105, 53), (1, 1), (4, 9)]
        for anterior, nova in casos:
            with self.subTest(anterior=anterior, nova=nova):
                diretorio.gravar_cache(
                    '"velho"', self.lista_de(anterior), VALIDADA_EM, self.cache
                )
                registro, codigo = self.rodar(
                    self.resultado(200, '"novo"', self.lista_de(nova))
                )
                self.assertEqual(codigo, 0)
                self.assertIsNone(registro["erro_tipo"])
                self.assertEqual(len(diretorio.ler_cache(self.cache)["lista"]), nova)

    def test_lista_curta_sem_lista_anterior_e_aceita(self):
        registro, codigo = self.rodar(self.resultado(200, '"novo"', self.lista_de(1)))
        self.assertEqual(codigo, 0)
        self.assertIsNone(registro["erro_tipo"])
        self.assertEqual(len(diretorio.ler_cache(self.cache)["lista"]), 1)

    def test_registro_segue_o_dicionario_e_acumula_em_lf(self):
        primeiro, _ = self.rodar(self.resultado(200, '"novo"', LISTA_NOVA, tentativas=2))
        segundo, _ = self.rodar(self.resultado(304, '"novo"'))
        self.assertEqual(
            set(primeiro),
            {
                "timestamp_utc",
                "status",
                "etag",
                "last_modified",
                "organizacoes",
                "tentativas",
                "usou_lista_anterior",
                "erro_tipo",
                "erro_detalhe",
                "problema_cache",
            },
        )
        self.assertEqual(primeiro["timestamp_utc"], "2026-11-03T12:00:00.000Z")
        self.assertEqual(primeiro["tentativas"], 2)
        self.assertEqual(primeiro["organizacoes"], 2)
        bruto = self.registro.read_bytes()
        self.assertNotIn(b"\r", bruto)
        linhas = bruto.decode("utf-8").splitlines()
        self.assertEqual([json.loads(linha) for linha in linhas], [primeiro, segundo])

    def test_falha_ao_registrar_sai_com_1_sem_derrubar(self):
        self.registro.mkdir()  # uma pasta no lugar do arquivo impede a abertura
        erros = io.StringIO()
        with contextlib.redirect_stderr(erros):
            _, codigo = self.rodar(self.resultado(200, '"novo"', LISTA_NOVA))
        self.assertEqual(codigo, 1)
        self.assertIn("falha ao gravar o registro", erros.getvalue())
        self.assertEqual(diretorio.ler_cache(self.cache)["etag"], '"novo"')

    def test_main_devolve_o_codigo_de_saida(self):
        registro = {
            "timestamp_utc": "t",
            "status": None,
            "organizacoes": None,
            "tentativas": 3,
            "usou_lista_anterior": False,
            "erro_tipo": "ConnectionError",
        }
        with patch.object(diretorio, "consultar_diretorio", return_value=(registro, 1)):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(diretorio.main(), 1)
