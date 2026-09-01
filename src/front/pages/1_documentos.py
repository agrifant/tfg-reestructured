import streamlit as st
import requests

# ------------------ VISTA 2: INFO ------------------

API_URL = "http://127.0.0.1:8002"

# ------------------ Funciones auexiliares ------------------
def mostrar_mensaje():
    if "mensaje" in st.session_state:
        tipo, texto = st.session_state.pop("mensaje")

        if tipo == "success":
            st.success(texto)
        elif tipo == "error":
            st.error(texto)
        elif tipo == "warning":
            st.warning(texto)
        elif tipo == "info":
            st.info(texto)

@st.dialog("Aviso")
def mensaje_aviso(name, value):

    mode = "activado" if value else "desactivado"

    st.warning(
        f"Has {mode} el mecanismo **{name}**.\n\n"
        "Ten en cuenta que los documentos procesados anteriormente "
        "fueron tratados teniendo en cuenta la configuración anterior. "
        "Se recomienda purgar la base de datos para aplicar correctamente "
        "la nueva configuración a todos los documentos."
    )

@st.dialog("Aviso")
def confirmacionEmbedding(new_embedding):
    st.warning(
            f"Esta acción eliminará todos los documentos de la base de datos."
            "Por ello, confirma que estas seguro de realizar esta acción"
        )
        
    if st.button("Confirmar", use_container_width=True):
        purgar_bd()
        change_embedding(new_embedding)
        st.rerun()



# ------------------ Api calls ------------------
def obtener_documentos(page, max_docs_pages):
    # Devuleve una lista con los documentos, numero de documentos totales 
    # guardados y cuantas páginas en total tienen
    try:
        res = requests.get(
            f"{API_URL}/documents",
            json={"page":page, "num_docs_page": max_docs_pages})
        
        if res.status_code == 200:
            docs_pagina = res.json().get("docs_pagina", [])
            total_docs = res.json().get("total_docs", 0)
            total_paginas = res.json().get("total_paginas", 0)

            return docs_pagina, total_docs, total_paginas
        
        else:
            st.error("Error al obtener documentos")
            return [] ,0 ,0
        
    except Exception:
        st.error("No se pudo conectar con la API")
        return [], 0, 0
    


def eliminar_documento(doc_id):
    try:
        res = requests.post(
            f"{API_URL}/deleteDocument",
            json={"id_documento": doc_id}
        )
        if res.status_code == 200:
            exito = res.json().get("respuesta", [])
                        
            if exito==True:
                st.session_state["mensaje"] = (
                    "success",
                    f"Documento añadido correctamente: {doc_id}"
                )
                st.rerun()
            else:
                st.session_state["mensaje"] = (
                    "error",
                    f"No se ha podido eliminar documento: {doc_id}"
                )
                st.rerun()
        else:
            st.session_state["mensaje"] = (
                "error",
                f"No se ha podido eliminar documento: {doc_id}"
            )
            st.rerun()
            
    except Exception:
        st.error("Error de conexión")


def purgar_bd():
    try:
        res = requests.post(f"{API_URL}/purgar")
        if res.status_code == 200:

            st.session_state["mensaje"] = (
                "success",
                f"Base de datos purgada"
            )
            
        else:
            st.session_state["mensaje"] = (
                "error",
                f"Error al purgar la base de datos"
            )

    except Exception:
        st.error("Error de conexión")


def añadir_documento(doc_id):
    try:
        res = requests.post(
            f"{API_URL}/addDocument",
            json={"id_documento": doc_id}
        )
        if res.status_code == 200:
            exito = res.json().get("respuesta", [])
            if exito==True:
                st.session_state["mensaje"] = (
                    "success",
                    f"Añadido correctamente documento: {doc_id}"
                )
                st.rerun()
                
            else:
                st.session_state["mensaje"] = (
                    "error",
                    f"Error al añaidir el documento: {doc_id}"
                )
                st.rerun()
        else:
            st.session_state["mensaje"] = (
                "error",
                f"Error al añaidir el documento: {doc_id}"
            )
            st.rerun()
            
    except Exception:
        st.error("Error de conexión")


def obtener_estado():
    #Devuleve el estado de delete y unificate
    try:
        res_del = requests.get(
            f"{API_URL}/mecanismoDelete"
        )

        res_un = requests.get(
            f"{API_URL}/mecanismoUnificate"
        )

        res_dim = requests.get(
            f"{API_URL}/dimensions"
        )

        if res_del.status_code == 200:
            delete=res_del.json()
        else:
            delete=False

        if res_un.status_code == 200:
            unificate=res_un.json()
        else:
            unificate=False

        if res_dim.status_code == 200:
            dimensions=res_dim.json()
        else:
            dimensions=0

        return delete, unificate, dimensions

    except Exception:
        st.error("Error de conexión")
    return False, False, 0


def change_delete():
    estado=st.session_state['boton_delete']

    try:
        requests.post(
            f"{API_URL}/mecanismoDelete",
            json={"value":estado})
        mensaje_aviso("Legal Pruning", estado)
    except Exception:
        st.error("Error de conexión")


def change_update():
    estado=st.session_state['boton_update']
    
    try:
        requests.post(
            f"{API_URL}/mecanismoUnificate",
            json={"value":estado})
        mensaje_aviso("Legal Version Update", estado)
    except Exception:
        st.error("Error de conexión")


def change_embedding(value):
 
    try:
        res=requests.post(
        f"{API_URL}/dimensions",
            json={"value":value})

        if res.status_code == 200:

            st.session_state["mensaje"] = (
                "success",
                f"Embedding cambiado a {value} dimensiones"
            )
            st.rerun()
        else:
            st.session_state["mensaje"] = (
                "error",
                f"Error cambiado a {value} dimensiones"
            )
            st.rerun()

    except Exception:
        st.error("Error de conexión")



# ------------------ UI ------------------
st.title("Gestión de documentos")

if "pagina" not in st.session_state:
    st.session_state.pagina = 1
    
documentos, total_docs, max_pages = obtener_documentos(st.session_state.pagina, 5)

# Obtener el estado inicial desde una función
delete, update, dimensions = obtener_estado()

st.session_state["boton_delete"] = delete
st.session_state["boton_update"] = update

#Mostramos los mensajes que hayan
mostrar_mensaje()

# Mostrar número de documentos
st.subheader(f"{total_docs} documentos guardados con embeddings de {dimensions} dimensiones")

st.divider()


# Botones de los mecanismos delete, unificate y purgar
col1, col2, col3 = st.columns(3)

with col1:
    # El toggle SOLO muestra el estado
    st.toggle(
        "Legal Pruning",
        value=delete,
        key="boton_delete",
        on_change=change_delete
    )


with col2:
    boton_update = st.toggle(
        "Legal Version Update",
        value=update,
        key="boton_update",
        on_change=change_update
    )


with col3:
    if st.button("Purgar base de datos"):
        purgar_bd()
        st.rerun()



col1, col2 = st.columns(2)

with col1:
    # Añadir documento
    st.subheader(f"Agregar nuevo documento")
    nuevo_doc = st.text_input("ID del documento a añadir")

    if st.button("Añadir documento"):
                if nuevo_doc:
                    añadir_documento(nuevo_doc)
                else:
                    st.warning("Introduce un ID")

with col2:
    st.subheader(f"Eliminar documento")
    del_doc = st.text_input("ID del documento a eliminar")

    if st.button("Eliminar documento"):
                if del_doc:
                    out = eliminar_documento(del_doc)
                else:
                    st.warning("Introduce un ID")

st.subheader(f"Cambiar dimensiones embeddings (Actual={dimensions})")
new_embedding = st.number_input(
    "Nuevas dimensiones del embedding",
    min_value=1,
    max_value=1024,
    value=None,
    step=1,
    placeholder="Introduce un número entre 1 y 1024"
)

if st.button(
    "Cambiar embedding",
    disabled=new_embedding is None
):
    confirmacionEmbedding(new_embedding)


st.divider()


# ------------------ Mostrar documentos paginación ------------------

st.subheader(f"Documentos guardados")

for doc in documentos:
    doc_id = doc if isinstance(doc, str) else doc.get("id", "unknown")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(doc_id)

    with col2:
        if st.button("Eliminar", key=doc_id):
            out = eliminar_documento(doc_id)

# ------------------ Botones Paginación ------------------

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Anterior") and st.session_state.pagina > 1:
        st.session_state.pagina -= 1
        st.rerun()

with col2:
    st.write(f"Página {st.session_state.pagina} de {max_pages}")

with col3:
    if st.button("Siguiente") and st.session_state.pagina < max_pages:
        st.session_state.pagina += 1
        st.rerun()