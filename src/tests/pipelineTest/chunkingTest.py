import unittest
import src.pipeline.chunking as chunking

def contar_tokens(texto):
    """Aproximación simple para los tests."""
    return len(texto.split())

# python3 -m tests.pipelineTest.chunkingTest
class TestFetcher(unittest.TestCase):

    def test_devuelve_lista(self):
        dic = {"id": "1",
                "texto": "Este es un texto corto para probar la función."}

        chunks = chunking.chunkear_diccionario(dic, "texto")

        self.assertIsInstance(chunks, list)
        self.assertGreaterEqual(len(chunks), 1)

    
    def test_division_por_saltos_de_linea(self):
        texto = (
            "Primera linea del documento.\n"
            "Segunda linea del documento.\n"
            "Tercera linea del documento."
        )

        dic = {"id": "1",
               "texto": texto}

        chunks = chunking.chunkear_diccionario(dic, label="texto", MAX_TOKENS=10, MIN_TOKENS=3)

        #print(chunks)
        self.assertGreaterEqual(len(chunks), 2)

    def test_division_por_letras(self):
        texto = (
            "Introducción larga que hace que el chunk supere el limite. "
            "a) Primer punto con bastante contenido para aumentar tokens. "
            "b) Segundo punto también con bastante contenido."
        )

        dic = {"id": "1",
               "texto": texto}

        chunks = chunking.chunkear_diccionario(dic, label="texto", MAX_TOKENS=20, MIN_TOKENS=3)

        self.assertGreaterEqual(len(chunks), 2)

    def test_division_por_puntos(self):
        texto = (
            "Esta es una frase muy larga que probablemente supere el límite. "
            "Esta es otra frase que también debería separarse. "
            "Y otra más para garantizar división."
        )

        dic = {"id": "1",
               "texto": texto}

        chunks = chunking.chunkear_diccionario(dic, label="texto", MAX_TOKENS=15, MIN_TOKENS=3)

        self.assertGreaterEqual(len(chunks), 2)

    def test_division_con_overlap(self):
        texto = " ".join(["palabra"] * 200)

        dic = {"id": "1",
               "texto": texto}

        chunks = chunking.chunkear_diccionario(
            dic,
            label="texto",
            MAX_TOKENS=50,
            MIN_TOKENS=20,
            OVERLAP=0.2
        )

        self.assertGreater(len(chunks), 1)

        texto_chunks = [c["cuerpo"] if isinstance(c, dict) else c for c in chunks]

        interseccion = set(texto_chunks[0].split()) & set(texto_chunks[1].split())

        self.assertGreater(len(interseccion), 0)

    def test_max_tokens_respetado(self):
        texto = " ".join(["token"] * 300)

        dic = {"id": "1", "texto": texto}

        chunks = chunking.chunkear_diccionario(dic, label="texto", MAX_TOKENS=50)

        for chunk in chunks:
            contenido = chunk["cuerpo"] if isinstance(chunk, dict) else chunk
            self.assertLessEqual(contar_tokens(contenido), 50+20)

    def test_estructura_chunk(self):
        texto = "Texto de prueba simple."

        dic = {"id": "1", "texto": texto}

        chunks = chunking.chunkear_diccionario(dic, label="texto")

        for chunk in chunks:
            self.assertIn("id", chunk)
            self.assertIn("cuerpo", chunk)
            self.assertIn("parte", chunk)
    
                

class SimpleTextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test._testMethodName)

class SimpleTextTestRunner(unittest.TextTestRunner):
    resultclass = SimpleTextTestResult

if __name__ == "__main__":
    unittest.main(testRunner=SimpleTextTestRunner(verbosity=2))
