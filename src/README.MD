# Estructura de `src`

En esta carpeta se encuentran todos los componentes que **constituyen el sistema RAG**. La estructura se organiza de la siguiente manera:

* **`actions/`**: Contiene los ficheros necesarios para la construcción y gestión de la API REST.

* **`bdController/`**: Contiene las funciones necesarias para gestionar la base de datos vectorial, así como para almacenar y recuperar la información.

* **`front/`**: Contiene los componentes correspondientes al frontend de la aplicación.

* **`llm/`**: Contiene las funciones necesarias para gestionar y comunicarse con el LLM.

* **`pipeline/`**: Contiene el proceso y las funciones necesarias para la **inserción y procesamiento de nuevos documentos** en el sistema RAG.

* **`rag/`**: Contiene la lógica encargada de integrar y coordinar las diferentes funcionalidades del sistema RAG.

* **`test/`**: Contiene las funciones y pruebas necesarias para evaluar el sistema RAG mediante **RAGAS**.

