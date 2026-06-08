import unittest
import bdController.chroma_db as chroma


# python3 -m tests.bdControllerTest.chroma
class TestFetcher(unittest.TestCase):
    def setUp(self):
        # Esto se ejecuta antes de cada test
        self.BD = chroma.chroma()
        self.BD.purge()

    def test_create_node(self):
        ids = ["id1", "id2"]
        content = ["texto 1", "texto 2"]
        metadata = [{"titulo": "Articulo 1"}, {"titulo": "Articulo 2"}]

        # Antes de crear nodos, no hay ninguno
        self.assertEqual(self.BD.countNodes(), 0)

        # Llamamos a createNodes
        self.BD.createNodes(ids, content, metadata)

        # Comprobamos que se han creado 2 nodos
        self.assertEqual(self.BD.countNodes(), 2)

        # Comprobamos que los ids y contenidos coinciden
        self.assertEqual(ids, ["id1", "id2"])
        self.assertEqual(content, ["texto 1", "texto 2"])

        # Comprobamos que la metadata se ha pasado correctamente
        self.assertEqual(metadata[0]["titulo"], "Articulo 1")
        self.assertEqual(metadata[1]["titulo"], "Articulo 2")

    def test_add_document(self):
        ids = [
            "id_1","id_2","id_3","id_4","id_5"
        ]
        content = [
            "content1","content2","content3","content4","content5"
        ]
        metadata = [
            {"meta": "metadata1"},
            {"meta": "metadata2"},
            {"meta": "metadata3"},
            {"meta": "metadata4"},
            {"meta": "metadata5"}
        ]

        # Antes de crear nodos, no hay nada
        self.assertEqual(self.BD.countNodes(), 0)

        # Llamada a createNodes con todos los argumentos
        resultado = self.BD.createNodes(ids, content, metadata)

        # Comprobamos resultados
        self.assertEqual(resultado, True)
        self.assertEqual(self.BD.countNodes(), 5)

    def test_deleteDocuments(self):
        ids = [
            "id_1","id_2","id_3","id_4","id_5"
        ]
        content = [
            "content1","content2","content3","content4","content5"
        ]
        metadata = [
            {"meta": "metadata1",
             "boe_id": "boe1"},
            {"meta": "metadata2",
             "boe_id": "boe1"},
            {"meta": "metadata3",
             "boe_id": "boe1"},
            {"meta": "metadata4",
             "boe_id": "boe2"},
            {"meta": "metadata5",
             "boe_id": "boe2"}
        ]

        self.assertEqual(self.BD.countNodes(), 0)
        self.assertEqual(self.BD.createNodes(ids,content, metadata), True)
        self.assertEqual(self.BD.countNodes(), 5)

        self.assertEqual(self.BD.deleteNode("id_7"),True)
        self.assertEqual(self.BD.deleteNode("id_2"),True)

        self.assertEqual(self.BD.deleteDocument("boe2"), True)
        self.assertEqual(self.BD.countNodes(), 2)

        self.assertEqual(self.BD.deleteDocument("boe1"), True)
        self.assertEqual(self.BD.countNodes(), 0)

class SimpleTextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test._testMethodName)

class SimpleTextTestRunner(unittest.TextTestRunner):
    resultclass = SimpleTextTestResult

if __name__ == "__main__":
    unittest.main(testRunner=SimpleTextTestRunner(verbosity=2))
