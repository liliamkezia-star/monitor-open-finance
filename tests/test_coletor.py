import unittest
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


if __name__ == "__main__":
    unittest.main()
