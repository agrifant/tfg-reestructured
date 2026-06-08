import src.Neo4j.gestorNeo4j as neo4j

datos_globales = {"id": "doc1", "fecha": "2026-03-12"}
materias = [{"id": "m1", "nombre": "materia1"}]
articulos = [
    ({"id": "a1", "titulo": "Artículo 1"}, [{"id": "a1.1", "cuerpo": "Chunk 1"}, {"id": "a1.2", "cuerpo": "Chunk 2"}])
]
disposiciones = []
texto_extra = []

exito = neo4j.generarDocumento(datos_globales, materias, articulos, disposiciones, texto_extra)
print("Éxito:", exito)