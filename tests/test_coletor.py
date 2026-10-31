import unittest
from datetime import datetime, timezone
from coletor import coletor


class TestCategoriaDoStatus(unittest.TestCase):

    def test_fronteiras_5xx(self):
        for status in (500, 503, 599):
            with self.subTest(status=status):
                self.assertEqual(coletor.categoria_do_status(status), "5xx")

    def test_fronteiras_4xx(self):
        for status in (400, 404, 499):
            with self.subTest(status=status):
                self.assertEqual(coletor.categoria_do_status(status), "4xx")

    def test_fronteiras_3xx(self):
        for status in (300, 301, 399):
            with self.subTest(status=status):
                self.assertEqual(coletor.categoria_do_status(status), "3xx")

    def test_rejeita_faixa_1xx(self):
        for status in (100, 199):
            with self.subTest(status=status):
                with self.assertRaises(coletor.RespostaMalformada):
                    coletor.categoria_do_status(status)


class TestSepararResposta(unittest.TestCase):

    def test_caminho_feliz(self):
        bytes_crus = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"X-Id-Sessao: 12345\r\n"
            b"\r\n"
            b'{"status": "ativo"}'
        )
        status, cabecalhos, corpo = coletor.separar_resposta(bytes_crus)

        self.assertEqual(status, 200)
        self.assertEqual(cabecalhos, {
            "content-type": "application/json",
            "x-id-sessao": "12345"
        })
        self.assertEqual(corpo, b'{"status": "ativo"}')

    def test_excecoes_de_estrutura(self):
        casos = [
            (b"HTTP/1.1 200 OK\r\nSem linha em branco no fim", "separador de cabeçalho ausente"),
            (b"HTTP/2 200 OK\r\n\r\n", "primeira linha não é HTTP/1.x"),
            (b"Bobeira qualquer\r\n\r\n", "primeira linha não é HTTP/1.x"),
            (b"HTTP/1.1\r\n\r\n", "primeira linha não é HTTP/1.x") # Cobre len(partes) < 2
        ]
        for bytes_crus, msg_esperada in casos:
            with self.subTest(bytes_crus=bytes_crus):
                with self.assertRaisesRegex(coletor.RespostaMalformada, msg_esperada):
                    coletor.separar_resposta(bytes_crus)

    def test_status_formato_e_faixa(self):
        # Validação do que saiu do teste 1xx: "20a" e "2000" falham no isdigit/len; "000" e "600" falham na faixa
        casos = [
            (b"HTTP/1.1 20 OK\r\n\r\n", "código de status inválido"),    # Menos de 3 caracteres
            (b"HTTP/1.1 20a OK\r\n\r\n", "código de status inválido"),   # Não numérico
            (b"HTTP/1.1 2000 OK\r\n\r\n", "código de status inválido"),  # Mais de 3 caracteres
            (b"HTTP/1.1 000 OK\r\n\r\n", "status fora da faixa HTTP"),   # isdigit() == True, mas < 100
            (b"HTTP/1.1 600 OK\r\n\r\n", "status fora da faixa HTTP"),   # isdigit() == True, mas > 599
            (b"HTTP/1.1 099 OK\r\n\r\n", "status fora da faixa HTTP")    # isdigit() == True, mas < 100
        ]
        for bytes_crus, msg_esperada in casos:
            with self.subTest(bytes_crus=bytes_crus):
                with self.assertRaisesRegex(coletor.RespostaMalformada, msg_esperada):
                    coletor.separar_resposta(bytes_crus)

    def test_status_nas_bordas_da_faixa(self):
        # Garante que as bordas da faixa de sucesso/validade são aceitas
        casos = [
            (b"HTTP/1.1 100 Continue\r\n\r\n", 100),
            (b"HTTP/1.1 599 Unknown Error\r\n\r\n", 599)
        ]
        for bytes_crus, status_esperado in casos:
            with self.subTest(status_esperado=status_esperado):
                status, _, _ = coletor.separar_resposta(bytes_crus)
                self.assertEqual(status, status_esperado)

    def test_bordas_cabecalhos_e_corpo(self):
        bytes_crus = (
            b"HTTP/1.1 200 OK\r\n"
            b"CABECALHO-MAIUSCULO: valor\r\n"          # Maiúsculas (deve virar minúscula)
            b"Date: Thu, 01 Jan 2026 12:00:00 GMT\r\n" # Valor com ':' (deve cortar só no primeiro)
            b"LinhaSemDoisPontosIgnorar\r\n"           # Linha sem ':' (deve ser ignorada)
            b"\r\n"
            b"Corpo falso com \r\n\r\n no meio"        # Múltiplos \r\n\r\n (find deve pegar o primeiro)
        )
        status, cabecalhos, corpo = coletor.separar_resposta(bytes_crus)

        # Compara o dicionário inteiro para garantir que chaves inválidas ou lixo não entraram
        self.assertEqual(cabecalhos, {
            "cabecalho-maiusculo": "valor",
            "date": "Thu, 01 Jan 2026 12:00:00 GMT"
        })
        self.assertEqual(corpo, b"Corpo falso com \r\n\r\n no meio")


class TestDecodificarChunked(unittest.TestCase):

    def test_caminho_feliz(self):
        casos = [
            (b"4\r\nWiki\r\n0\r\n\r\n", b"Wiki"),                                # Único pedaço
            (b"4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n", b"Wikipedia"),             # Múltiplos pedaços
            (b"0\r\n\r\n", b"")                                                  # Corpo vazio
        ]
        for corpo_cru, esperado in casos:
            with self.subTest(corpo_cru=corpo_cru):
                self.assertEqual(coletor.decodificar_chunked(corpo_cru), esperado)

    def test_tamanho_em_hexadecimal(self):
        # Garante que as letras a-f e A-F são avaliadas na base 16 (10 bytes)
        self.assertEqual(coletor.decodificar_chunked(b"a\r\n0123456789\r\n0\r\n\r\n"), b"0123456789")
        self.assertEqual(coletor.decodificar_chunked(b"A\r\n0123456789\r\n0\r\n\r\n"), b"0123456789")

    def test_extensao_de_chunk_ignorada(self):
        # A presença de ';' e parâmetros na mesma linha do tamanho não deve quebrar o parse
        corpo_cru = b"4;nome=valor;outro_parametro\r\nWiki\r\n0\r\n\r\n"
        self.assertEqual(coletor.decodificar_chunked(corpo_cru), b"Wiki")

    def test_excecoes_de_estrutura(self):
        casos = [
            # 1. Não acha o próximo \r\n do loop (ex: a conexão caiu antes de enviar o 0 final)
            (b"4\r\nWiki\r\n", "chunked sem o pedaço final de tamanho 0"),

            # 2. O tamanho declarado não é um hexadecimal válido
            (b"G\r\nWiki\r\n0\r\n\r\n", "tamanho de pedaço inválido"),

            # 3. Dados a menos: declara 5, mas envia 4 bytes.
            # O código vai procurar o \r\n 5 bytes depois e achar um pedaço do '0\r\n'
            (b"5\r\nWiki\r\n0\r\n\r\n", "pedaço truncado ou sem CRLF no fim"),

            # 4. Dados a mais: declara 3, mas envia 4 bytes.
            # O código vai procurar o \r\n 3 bytes depois e trombar na letra 'i'
            (b"3\r\nWiki\r\n0\r\n\r\n", "pedaço truncado ou sem CRLF no fim")
        ]
        for corpo_cru, msg_esperada in casos:
            with self.subTest(corpo_cru=corpo_cru):
                with self.assertRaisesRegex(coletor.CorpoInvalido, msg_esperada):
                    coletor.decodificar_chunked(corpo_cru)

    def test_rejeita_tamanho_fora_da_rfc(self):
        # O int(x, 16) aceita prefixos, sinais e '_' que a RFC 9112 proíbe (1*HEXDIG).
        for tamanho in (b"+a", b"0xa", b"1_0", b"-2"):
            with self.subTest(tamanho=tamanho):
                corpo_cru = tamanho + b"\r\n0123456789\r\n0\r\n\r\n"
                with self.assertRaisesRegex(coletor.CorpoInvalido, "tamanho de pedaço inválido"):
                    coletor.decodificar_chunked(corpo_cru)


class TestExtrairCorpo(unittest.TestCase):

    def test_caminhos_de_sucesso(self):
        # 1. Chunked (ignora Content-Length se presente)
        corpo_chunked = b"4\r\nWiki\r\n0\r\n\r\n"
        self.assertEqual(coletor.extrair_corpo({"transfer-encoding": "chunked"}, corpo_chunked), b"Wiki")

        # 2. Content-Length exato
        self.assertEqual(coletor.extrair_corpo({"content-length": "4"}, b"Wiki"), b"Wiki")

        # 3. Nenhum dos dois (retorna cru)
        self.assertEqual(coletor.extrair_corpo({}, b"Wiki"), b"Wiki")

    def test_chunked_vence_content_length(self):
        # A RFC diz que se ambos vierem, Transfer-Encoding anula o Content-Length
        cabecalhos = {"transfer-encoding": "chunked", "content-length": "999"} # 999 está totalmente errado
        corpo_chunked = b"4\r\nWiki\r\n0\r\n\r\n"
        self.assertEqual(coletor.extrair_corpo(cabecalhos, corpo_chunked), b"Wiki")

    def test_transfer_encoding_multiplo_e_maiusculas(self):
        corpo_chunked = b"4\r\nWiki\r\n0\r\n\r\n"

        # Maiúsculas com espaços extras (normalizados pelo .lower e .strip)
        self.assertEqual(coletor.extrair_corpo({"transfer-encoding": " CHUNKED "}, corpo_chunked), b"Wiki")

        # 'gzip, chunked': o envelope de fora (último) é chunked, então decodifica
        self.assertEqual(coletor.extrair_corpo({"transfer-encoding": "gzip, chunked"}, corpo_chunked), b"Wiki")

        # 'chunked, gzip': o envelope de fora é gzip. Não entra no if do chunked e retorna o corpo cru.
        self.assertEqual(coletor.extrair_corpo({"transfer-encoding": "chunked, gzip"}, b"binario_gzip_falso"), b"binario_gzip_falso")

    def test_excecoes_content_length(self):
        casos = [
            ({"content-length": "abc"}, b"123", "Content-Length inválido"),
            ({"content-length": "5"}, b"1234", "Content-Length declara"), # Corpo menor que o declarado
            ({"content-length": "3"}, b"1234", "Content-Length declara")  # Corpo maior que o declarado
        ]
        for cabecalhos, corpo, msg_esperada in casos:
            with self.subTest(cabecalhos=cabecalhos):
                with self.assertRaisesRegex(coletor.CorpoInvalido, msg_esperada):
                    coletor.extrair_corpo(cabecalhos, corpo)

    def test_rejeita_content_length_fora_da_rfc(self):
        # "-1" não é 1*DIGIT. "¹²³" chegam pela rede (bytes 0xB9, 0xB2, 0xB3 em latin-1)
        # e têm isdigit() == True, mas o int() não os aceita.
        for declarado in ("-1", "¹", "²", "³"):
            with self.subTest(declarado=declarado):
                with self.assertRaisesRegex(coletor.CorpoInvalido, "Content-Length inválido"):
                    coletor.extrair_corpo({"content-length": declarado}, b"")


class TestEJson(unittest.TestCase):

    def test_basico_e_vazio(self):
        # Casos óbvios
        self.assertTrue(coletor.e_json(b'{"status": "ativo"}'))
        self.assertFalse(coletor.e_json(b'texto plano sem formato'))
        self.assertFalse(coletor.e_json(b''))  # Vazio lança JSONDecodeError

    def test_codificacao_invalida(self):
        # \x80 não é UTF-8 válido. Lança UnicodeDecodeError.
        # Como UnicodeDecodeError herda de ValueError, o except segura a exceção.
        self.assertFalse(coletor.e_json(b'\x80'))

    def test_tipos_primitivos(self):
        # Primitivos soltos são JSON válido (RFC 8259); se servem ao endpoint é conformidade (A2.3)
        self.assertTrue(coletor.e_json(b'null'))
        self.assertTrue(coletor.e_json(b'1'))
        self.assertTrue(coletor.e_json(b'"texto"'))

    def test_rejeita_constantes_fora_da_rfc(self):
        # O json.loads do Python aceita NaN e Infinity por padrão, mas a RFC 8259 não
        for corpo in (b'NaN', b'Infinity', b'-Infinity', b'[1, NaN]'):
            with self.subTest(corpo=corpo):
                self.assertFalse(coletor.e_json(corpo))

    def test_aninhamento_profundo_nao_derruba(self):
        # Um JSON maliciosamente ou acidentalmente aninhado lança RecursionError, que não é ValueError.
        # O limite real depende da versão do Python (2000 níveis passam no 3.12), daí a folga grande.
        corpo_profundo = b'[' * 100_000 + b']' * 100_000
        self.assertFalse(coletor.e_json(corpo_profundo))


class TestTempo(unittest.TestCase):

    def test_ciclo_de_bordas(self):
        casos = [
            # Início exato do bloco
            (datetime(2026, 10, 31, 12, 0, 0, 0, tzinfo=timezone.utc),
             datetime(2026, 10, 31, 12, 0, 0, 0, tzinfo=timezone.utc)),

            # Fim extremo do primeiro bloco (não avança a hora)
            (datetime(2026, 10, 31, 12, 14, 59, 999999, tzinfo=timezone.utc),
             datetime(2026, 10, 31, 12, 0, 0, 0, tzinfo=timezone.utc)),

            # Início exato do segundo bloco
            (datetime(2026, 10, 31, 12, 15, 0, 0, tzinfo=timezone.utc),
             datetime(2026, 10, 31, 12, 15, 0, 0, tzinfo=timezone.utc)),

            # Último bloco da hora
            (datetime(2026, 10, 31, 12, 45, 0, 0, tzinfo=timezone.utc),
             datetime(2026, 10, 31, 12, 45, 0, 0, tzinfo=timezone.utc)),

            # Fim extremo do último bloco da hora
            (datetime(2026, 10, 31, 12, 59, 59, 999999, tzinfo=timezone.utc),
             datetime(2026, 10, 31, 12, 45, 0, 0, tzinfo=timezone.utc))
        ]

        for instante, inicio_esperado in casos:
            with self.subTest(instante=instante):
                self.assertEqual(coletor.ciclo_de(instante), inicio_esperado)

    def test_ciclo_de_virada_de_dia(self):
        # Garante que os últimos microssegundos do ano ficam no último bloco do ano,
        # sem alterar dia, mês ou ano acidentalmente.
        instante = datetime(2026, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
        esperado = datetime(2026, 12, 31, 23, 45, 0, 0, tzinfo=timezone.utc)

        self.assertEqual(coletor.ciclo_de(instante), esperado)

    def test_formatar_utc_truncamento(self):
        # 999999 microssegundos. Se isoformat() arredondasse para cima, isso viraria 12:15:00.
        # Mas em Python, isoformat trunca.
        instante = datetime(2026, 10, 31, 12, 14, 59, 999999, tzinfo=timezone.utc)

        # Teste timespec = milliseconds (Padrão)
        str_ms = coletor.formatar_utc(instante)
        self.assertEqual(str_ms, "2026-10-31T12:14:59.999Z")

        # Teste timespec = seconds
        str_sec = coletor.formatar_utc(instante, timespec="seconds")
        self.assertEqual(str_sec, "2026-10-31T12:14:59Z")

    def test_ciclo_utc_composto(self):
        # Como o registro monta o ciclo_utc; comparar texto confere também o "Z"
        instante = datetime(2026, 10, 31, 12, 14, 59, 999999, tzinfo=timezone.utc)
        self.assertEqual(coletor.formatar_utc(coletor.ciclo_de(instante), timespec="seconds"),
                         "2026-10-31T12:00:00Z")


class TestVersaoMajorDe(unittest.TestCase):

    def test_caminho_feliz(self):
        casos = [
            ("https://api.crefisa.com.br/opendata-loans/v1/personal-loans", 1),
            ("https://api.banco.com.br/open-banking/v12/recurso", 12),
            ("https://api.banco.com.br/open-banking/v01/recurso", 1)  # O int("01") resolve o zero à esquerda
        ]
        for url, versao_esperada in casos:
            with self.subTest(url=url):
                self.assertEqual(coletor.versao_major_de(url), versao_esperada)

    def test_excecoes(self):
        casos = [
            "https://api.banco.com.br/opendata-loans/personal-loans",  # Sem versão
            "https://api.banco.com.br/opendata-loans/v1"               # Sem a barra no final (a regex exige /vN/)
        ]
        for url in casos:
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "URL sem /vN/ no caminho"):
                    coletor.versao_major_de(url)


if __name__ == "__main__":
    unittest.main()
