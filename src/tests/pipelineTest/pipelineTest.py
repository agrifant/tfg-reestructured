import unittest
from unittest.mock import patch, MagicMock
import src.pipeline.pipeline as pipeline

# python3 -m tests.pipelineTest.pipelineTest
class TestFetcher(unittest.TestCase):
    def test_devuelve_estructura_correcta(self):
        # Mock del archivo XML
        mock_xml = MagicMock()

        with patch("src.pipeline.fetcher.obtenerXML", return_value=mock_xml), \
             patch("src.pipeline.parser.obtenerArticulos", return_value=([{"id":"1","cuerpo":"Texto"}], [], [])), \
             patch("src.pipeline.parser.obtenerDatosGlobales", return_value=({"fecha":"2026-03-12"}, ["materia1"])), \
             patch("src.pipeline.chunking.chunkear_diccionario", return_value=[{"id":"1.1","cuerpo":"Texto","parte":"Parte 1 de 1"}]):

            datos_globales, materias, articulos_chunked, disposiciones_chunked, texto_extra_chunked = pipeline.pipeline("doc_demo.xml")

            self.assertIsInstance(datos_globales, dict)
            self.assertIsInstance(materias, list)
            self.assertIsInstance(articulos_chunked, list)
            self.assertIsInstance(disposiciones_chunked, list)
            self.assertIsInstance(texto_extra_chunked, list)

            # Comprobar que cada chunk es un diccionario
            for _, chunks in articulos_chunked:
                self.assertIsInstance(chunks, list)
                for c in chunks:
                    self.assertIn("cuerpo", c)
                    self.assertIn("id", c)
                    self.assertIn("parte", c)

class SimpleTextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test._testMethodName)

class SimpleTextTestRunner(unittest.TextTestRunner):
    resultclass = SimpleTextTestResult

if __name__ == "__main__":
    unittest.main(testRunner=SimpleTextTestRunner(verbosity=2))
