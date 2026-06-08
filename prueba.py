import src.rag.rag as rag
import src.llm.callToLLM as llm


boe1 = 'BOE-A-1993-20748'
boe2 = 'BOE-A-2015-10565'

#Inicializamos el rag
maquina1 = rag.rag("default", 0 , True)

maquina1.purgarBasesDatos()
maquina1.newBoeDocument(boe1)
input()
maquina1.newBoeDocument(boe2)


prompt="""
1. Quedan derogadas todas las normas de igual o inferior rango en lo que contradigan o se opongan a lo dispuesto en la presente Ley. 2. Quedan derogadas expresamente las siguientes disposiciones: a) Ley 30/1992, de 26 de noviembre, de Régimen Jurídico de las Administraciones Públicas y del Procedimiento Administrativo Común. b) Ley 11/2007, de 22 de junio, de acceso electrónico de los ciudadanos a los Servicios Públicos. c) Los artículos 4 a 7 de la Ley 2/2011, de 4 de marzo, de Economía Sostenible. d) Real Decreto 429/1993, de 26 de marzo, por el que se aprueba el Reglamento de los procedimientos de las Administraciones Públicas en materia de responsabilidad patrimonial. e) Real Decreto 1398/1993, de 4 de agosto, por el que se aprueba el Reglamento del Procedimiento para el Ejercicio de la Potestad Sancionadora. f) Real Decreto 772/1999, de 7 de mayo, por el que se regula la presentación de solicitudes, escritos y comunicaciones ante la Administración General del Estado, la expedición de copias de documentos y devolución de originales y el régimen de las oficinas de registro. "
g) Los artículos 2.3, 10, 13, 14, 15, 16, 26, 27, 28, 29.1.a), 29.1.d), 31, 32, 33, 35, 36, 39, 48, 50, los apartados 1, 2 y 4 de la disposición adicional primera, la disposición adicional tercera, la disposición transitoria primera, la disposición transitoria segunda, la disposición transitoria tercera y la disposición transitoria cuarta del Real Decreto 1671/2009, de 6 de noviembre, por el que se desarrolla parcialmente la Ley 11/2007, de 22 de junio, de acceso electrónico de los ciudadanos a los Servicios Públicos. Hasta que, de acuerdo con lo dispuesto en la disposición final séptima, produzcan efectos las previsiones relativas al registro electrónico de apoderamientos, registro electrónico, punto de acceso general electrónico de la Administración y archivo único electrónico, se mantendrán en vigor los artículos de las normas previstas en las letras a), b) y g) relativos a las materias mencionadas. 3. Las referencias contenidas en normas vigentes a las disposiciones que se derogan expresamente deberán entenderse efectuadas a las disposiciones de esta Ley que regulan la misma materia que aquéllas.
"""
"""
data=llm.askDerrogated(prompt)
for i in data:
    print(i)
    print("\n")
"""