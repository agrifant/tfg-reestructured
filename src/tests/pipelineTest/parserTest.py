
#def obtenerDatosGlobales(boe_XML: BytesIO)->tuple[dict, dict]:
#
#def obtenerArticulos(boe_XML: BytesIO, boe: str)-> tuple[list[dict], list[dict], list[dict]]:

# python3 -m tests.pipelineTest.parserTest

import unittest
import src.pipeline.parser as parser
from io import BytesIO

solo_articulos="""<?xml version="1.0" encoding="UTF-8"?>
<documento fecha_actualizacion="20260130132601">
  <texto>
    <p class="articulo">Artículo 1</p>
    <p class="parrafo">Texto artículo 1.</p>
    <p class="articulo">Artículo 2</p>
    <p class="parrafo">Texto artículo 2.</p>
  </texto>
</documento>"""

solo_disposiciones="""<?xml version="1.0" encoding="UTF-8"?>
<documento fecha_actualizacion="20260130132601">
  <texto>
    <p class="articulo">Disposición 1</p>
    <p class="parrafo">Texto disposición 1.</p>
  </texto>
</documento>"""

solo_texto_extra="""<?xml version="1.0" encoding="UTF-8"?>
<documento fecha_actualizacion="20260130132601">
  <texto>
    <p class="parrafo_2">Texto extra 1</p>
    <p class="parrafo_2">Texto extra 2</p>
  </texto>
</documento>"""

mix="""<?xml version="1.0" encoding="UTF-8"?>
<documento fecha_actualizacion="20260130132601">
  <texto>
    <p class="parrafo_2">Texto extra 1</p>
    <p class="parrafo_2">Texto extra 2</p>
    <p class="articulo">Artículo 1</p>
    <p class="parrafo">Texto artículo 1.</p>
    <p class="titulo_num">TÍTULO PRELIMINAR</p>
    <p class="titulo_tit">Disposiciones generales</p>
    <p class="parrafo">Texto extra 3</p>
    <p class="articulo">Artículo 2</p>
    <p class="parrafo">Texto artículo 2.</p>
    <p class="articulo">Disposición 1</p>
    <p class="parrafo">Texto disposición 1.</p>
  </texto>
</documento>"""

# python3 -m tests.pipelineTest.FetcherTests
class TestFetcher(unittest.TestCase):

    # Caso correcto con sólo artículos
    def test_parser_obtener_articulos_solo_articulos(self):
        texto_prueba=BytesIO(solo_articulos.encode("utf-8"))
        articulos, disposiciones, texto_extra = parser.obtenerArticulos(texto_prueba, "BOE-A-1978-31229")

        # Devuelve 3 listas
        self.assertIsInstance(articulos, list)
        self.assertIsInstance(disposiciones, list)
        self.assertIsInstance(texto_extra, list)

        # Deben contener el número esperado de elementos
        self.assertEqual(len(articulos), 2)
        self.assertEqual(len(texto_extra), 0)
        self.assertEqual(len(disposiciones), 0)

        # Primer artículo
        self.assertEqual(articulos[0]["titulo_articulo"], "Artículo 1")
        self.assertEqual(articulos[0]["cuerpo"].strip(), "Texto artículo 1.")

        # Segundo artículo
        self.assertEqual(articulos[1]["titulo_articulo"], "Artículo 2")
        self.assertEqual(articulos[1]["cuerpo"].strip(), "Texto artículo 2.")


    # Caso correcto con sólo disposiciones
    def test_parser_obtener_articulos_solo_disposiciones(self):
        texto_prueba=BytesIO(solo_disposiciones.encode("utf-8"))
        articulos, disposiciones, texto_extra = parser.obtenerArticulos(texto_prueba, "BOE-A-1978-31229")

        # Devuelve 3 listas
        self.assertIsInstance(articulos, list)
        self.assertIsInstance(disposiciones, list)
        self.assertIsInstance(texto_extra, list)

        # Deben contener el número esperado de elementos
        self.assertEqual(len(articulos), 0)
        self.assertEqual(len(texto_extra), 0)
        self.assertEqual(len(disposiciones), 1)

        # Primera disposicion
        self.assertEqual(disposiciones[0]["titulo_articulo"], "Disposición 1")
        self.assertEqual(disposiciones[0]["cuerpo"], "Texto disposición 1.")


    # Caso correcto con sólo texto_extra
    def test_parser_obtener_articulos_solo_texto_extra(self):
        texto_prueba=BytesIO(solo_texto_extra.encode("utf-8"))
        articulos, disposiciones, texto_extra = parser.obtenerArticulos(texto_prueba, "BOE-A-1978-31229")

        # Devuelve 3 listas
        self.assertIsInstance(articulos, list)
        self.assertIsInstance(disposiciones, list)
        self.assertIsInstance(texto_extra, list)

        # Deben contener el número esperado de elementos
        self.assertEqual(len(articulos), 0)
        self.assertEqual(len(texto_extra), 1)
        self.assertEqual(len(disposiciones), 0)

        # Texto extra
        self.assertEqual(texto_extra[0]["cuerpo"].strip(), "Texto extra 1\nTexto extra 2")


    # Caso correcto con un mix de todo
    def test_parser_obtener_articulos_mix_todo(self):
        texto_prueba=BytesIO(mix.encode("utf-8"))
        articulos, disposiciones, texto_extra = parser.obtenerArticulos(texto_prueba, "BOE-A-1978-31229")

        # Devuelve 3 listas
        self.assertIsInstance(articulos, list)
        self.assertIsInstance(disposiciones, list)
        self.assertIsInstance(texto_extra, list)

        # Deben contener el número esperado de elementos
        self.assertEqual(len(articulos), 2)
        self.assertEqual(len(texto_extra), 2)
        self.assertEqual(len(disposiciones), 1)

        # Primer artículo
        self.assertEqual(articulos[0]["titulo_articulo"], "Artículo 1")
        self.assertEqual(articulos[0]["cuerpo"].strip(), "Texto artículo 1.")

        # Segundo artículo
        self.assertEqual(articulos[1]["titulo_articulo"], "Artículo 2")
        self.assertEqual(articulos[1]["cuerpo"].strip(), "Texto artículo 2.")

        # Primera disposicion
        self.assertEqual(disposiciones[0]["titulo_articulo"], "Disposición 1")
        self.assertEqual(disposiciones[0]["cuerpo"], "Texto disposición 1.")

        # Texto extra
        self.assertEqual(texto_extra[0]["cuerpo"].strip(), "Texto extra 1\nTexto extra 2")
        self.assertEqual(texto_extra[1]["cuerpo"].strip(), "Texto extra 3")        

    
    

class SimpleTextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test._testMethodName)

class SimpleTextTestRunner(unittest.TextTestRunner):
    resultclass = SimpleTextTestResult

if __name__ == "__main__":
    unittest.main(testRunner=SimpleTextTestRunner(verbosity=2))





















#"""
#def test_parser_basic_case():
#    xml = """
#    <boe>
#        <disposicion>
#            <titulo>Resolución X</titulo>
#            <fecha>2024-01-03</fecha>
#        </disposicion>
#    </boe>
#    """
#
#    result = parse_boe(xml)
#
#    assert isinstance(result, list)
#    assert result[0]["titulo"] == "Resolución X"
#    assert result[0]["fecha"] == "2024-01-03"
#
#def test_parser_multiple_entries():
#    xml = """
#    <boe>
#        <disposicion><titulo>A</titulo></disposicion>
#        <disposicion><titulo>B</titulo></disposicion>
#    </boe>
#    """
#
#    result = parse_boe(xml)
#
#    assert len(result) == 2
#    assert result[1]["titulo"] == "B"
#
#def test_parser_missing_optional_field():
#    xml = """
#    <boe>
#        <disposicion>
#            <titulo>Resolución sin fecha</titulo>
#        </disposicion>
#    </boe>
#    """
#
#    result = parse_boe(xml)
#
#    assert result[0]["titulo"] == "Resolución sin fecha"
#    assert result[0].get("fecha") is None
#
##Devuelve excepción? lista vacía?
#def test_parser_invalid_xml():
#    invalid_xml = "<boe><disposicion></boe>"
#
#    with pytest.raises(ParseError):
#        parse_boe(invalid_xml)
#
#
#def test_output_schema():
#    xml = load_fixture("boe_simple.xml")
#    result = parse_boe(xml)
#
#    for item in result:
#        assert set(item.keys()) == {
#            "id_boe",
#            "titulo",
#            "fecha",
#            "organismo"
#        }
#
#def test_parser_real_xml_fixture():
#    with open("tests/fixtures/boe_real_1.xml") as f:
#        xml = f.read()
#
#    result = parse_boe(xml)
#
#    assert len(result) > 0
#    assert "titulo" in result[0]
#
#"""