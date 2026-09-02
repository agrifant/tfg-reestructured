# RAG autodepurado sobre la legislación española.

## Descripción

Este trabajo desarrolla un sistema **RAG (Retrieval-Augmented Generation)** 
cuya fuente de información está constituida por documentos del **Boletín Oficial del Estado (BOE)**. 
El sistema permite incorporar nuevos documentos a partir de su identificador (ID) y 
realizar pruebas utilizando diferentes mecanismos de recuperación y actualización de 
la información, con el objetivo de analizar y comparar su comportamiento.

El sistema implementa tres mecanismos principales:

* **Legal Pruning:** elimina automáticamente la información que ha 
dejado de estar vigente en la legislación española, evitando 
que contenido obsoleto sea utilizado durante la recuperación.

* **Legal Version Update:** genera automáticamente una versión 
actualizada de los documentos a partir de las modificaciones 
introducidas en la legislación.

* **Similarity Threshold Filtering:** permite establecer el nivel mínimo 
de similitud que deben alcanzar los *chunks* recuperados para ser 
considerados relevantes por el sistema.

# Instalación

Para utilizar este software es necesario disponer de 
Ollama y del modelo Llama 3.1 de 8B, que será utilizado 
por el sistema RAG para realizar las consultas al modelo de lenguaje.

1. Instalar Ollama

Instala Ollama siguiendo las instrucciones correspondientes a tu sistema operativo.

Una vez instalado, descarga el modelo Llama 3.1 de 8B

Durante la ejecución del sistema, Ollama debe estar disponible y ejecutándose,
ya que RAG Legislativo lo utiliza para realizar las consultas al modelo de lenguaje.

2. Instalar las dependencias

Desde el directorio raíz del proyecto, instala las dependencias necesarias mediante:

pip install -r requirements.txt

# Despliegue

El proyecto incluye el script start.sh, encargado de iniciar 
los diferentes servicios necesarios para el funcionamiento de RAG Legislativo.

Antes de ejecutarlo, es necesario darle permisos de ejecución:

chmod u+x start.sh

A continuación, se puede iniciar el sistema mediante:

./start.sh

Una vez iniciado el sistema, la interfaz de Streamlit estará disponible en:

http://localhost:8501

encargado de la interfaz web para interactuar con el sistema.

La API estará disponible en:

http://localhost:8002

encargado de gestionar la lógica y las consultas del sistema RAG. 

y ChromaDB en:

http://localhost:8001

siendo base de datos vectorial utilizada para almacenar y recuperar los documentos y chunks. 




## Estructura del proyecto

La estructura principal del proyecto se organiza de la siguiente manera:

```text
proyecto/
├── data/
├── results/
├── src/
└── test/
```

* **`data/`**: contiene el conjunto de datos utilizado para realizar las pruebas y evaluaciones del sistema desarrolladas en el TFG.

* **`results/`**: almacena los resultados obtenidos durante la ejecución de las diferentes pruebas y experimentos realizados.

* **`src/`**: contiene el código fuente de la aplicación y la implementación de los diferentes componentes del sistema RAG.

* **`test/`**: contiene las pruebas utilizadas para comprobar el correcto funcionamiento de los diferentes componentes del sistema.