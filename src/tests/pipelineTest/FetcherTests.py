import unittest
import src.pipeline.fetcher as fetcher
from unittest.mock import patch
from io import BytesIO
import requests

# python3 -m tests.pipelineTest.FetcherTests
class TestFetcher(unittest.TestCase):

    # Caso correcto, devuelve el xml
    @patch("src.pipeline.fetcher.requests.get")
    def test_fetcher_returns_xml(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"<xml>data</xml>"

        result = fetcher.obtenerXML("BOE-A-2024-1234")

        assert isinstance(result, BytesIO)
        assert result.read() == b"<xml>data</xml>"

    # Caso de error status =! 200
    @patch("src.pipeline.fetcher.requests.get")
    def test_fetcher_status_not_equal_200(self, mock_get):
        mock_get.return_value.status_code = 404

        result = fetcher.obtenerXML("BOE-A-2024-1234")

        assert result is None

    # Caso en el que el contenido leido está vacío
    @patch("src.pipeline.fetcher.requests.get")
    def test_fetcher_empty_content(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b""

        result = fetcher.obtenerXML("BOE-A-2024-1234")
        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.read(), b"")

    # Caso en el que nos de un error de conexión
    @patch("src.pipeline.fetcher.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_fetcher_raises_connection_error(self, mock_get):
        result = fetcher.obtenerXML("BOE-A-2024-1234")
        self.assertIsNone(result)
        

    # Caso en el que expira el tiempo límite de espera
    @patch("src.pipeline.fetcher.requests.get", side_effect=requests.Timeout)
    def test_fetcher_timeout(self, mock_get):
        result = fetcher.obtenerXML("BOE-A-2024-1234")
        self.assertIsNone(result)
    
    # Caso en el que llama a la función correcta
    @patch("src.pipeline.fetcher.requests.get")
    def test_fetcher_calls_correct_url(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"<xml>data</xml>"

        num_boe = "BOE-A-2024-1234"
        fetcher.obtenerXML(num_boe)
        mock_get.assert_called_once()  
        called_url = mock_get.call_args[0][0] 
        self.assertEqual(called_url, f"https://www.boe.es/diario_boe/xml.php?id={num_boe}")

    # Caso de inputs inválidos
    @patch("src.pipeline.fetcher.requests.get")
    def test_fetcher_invalid_num_boe(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"<xml>data</xml>"

        result = fetcher.obtenerXML("")
        self.assertIsInstance(result, BytesIO)

    # Caso real
    def test_fetcher_real(self):
        xml_file = fetcher.obtenerXML("BOE-A-2024-1234")
        self.assertTrue(xml_file.read().decode("utf-8").startswith("<?xml"))

class SimpleTextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test._testMethodName)

class SimpleTextTestRunner(unittest.TextTestRunner):
    resultclass = SimpleTextTestResult

if __name__ == "__main__":
    unittest.main(testRunner=SimpleTextTestRunner(verbosity=2))