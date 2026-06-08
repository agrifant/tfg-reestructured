import src.Neo4j.Neo4jConnection as neo4j

# python3 -m tests.otros.grafos2
BD =neo4j.Neo4jConnection()
BD.purge()
BD.close()
"""
operaciones = [
    ("Global", {"id": "1", "fecha": "2026-03-12"}),
    ("Materia", {"id": "m1", "nombre": "materia1"}),
    ("Articulo", {"id": "a1", "cuerpo": "Texto del artículo"})
]
BD =neo4j.Neo4jConnection()

exito = BD.create_nodes(operaciones)
if not exito:
    print("La creación de nodos falló, todo fue revertido.")

BD.close()
"""