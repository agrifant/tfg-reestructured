import streamlit as st
import requests

# ------------------ VISTA 2: INFO ------------------

API_URL = "http://127.0.0.1:8002"

# ------------------ API CALLS ------------------
def obtener_documentos():
    #Modificar api para solo devolver los de la paginación
    try:
        res = requests.get(f"{API_URL}/documents")
        if res.status_code == 200:
            return res.json()
        else:
            st.error("Error al obtener documentos")
            return []
    except Exception:
        st.error("No se pudo conectar con la API")
        return []


def eliminar_documento(doc_id):
    try:
        res = requests.post(
            f"{API_URL}/deleteDocument",
            json={"id_documento": doc_id}
        )
        if res.status_code == 200:
            st.success(f"{doc_id} eliminado")
        else:
            st.error("Error al eliminar")
    except Exception:
        st.error("Error de conexión")


def purgar_bd():
    try:
        res = requests.post(f"{API_URL}/purgar")
        if res.status_code == 200:
            st.rerun()
        else:
            st.error("Error al purgar")
    except Exception:
        st.error("Error de conexión")


def añadir_documento(doc_id):
    try:
        res = requests.post(
            f"{API_URL}/addDocument",
            json={"id_documento": doc_id}
        )
        if res.status_code == 200:
            st.rerun()
        else:
            st.error("Error al añadir")
    except Exception:
        st.error("Error de conexión")

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

    if st.button("Entendido", use_container_width=True):
        st.rerun()


def obtener_estado():
    #Añadir api del backend
    return True, True


def change_delete():
    #Añadir api del backend
    estado=st.session_state['boton_delete']
    mensaje_aviso("Legal Pruning", estado)

    print(f"Delete {estado}")


def change_update():
    #Añadir api del backend
    estado=st.session_state['boton_update']
    mensaje_aviso("Legal Version Update", estado)
    
    print(f"Update {estado}")


# ------------------ UI ------------------
st.title("Gestión de documentos")

documentos = obtener_documentos()
total_docs = len(documentos)


# Obtener el estado inicial desde una función
delete, update = obtener_estado()


# Botones de los mecanismos delete y unificate
col1, col2 = st.columns(2)

with col1:
    # El toggle SOLO muestra el estado
    st.toggle(
        "Delete",
        value=delete,
        key="boton_delete",
        on_change=change_delete
    )


with col2:
    boton_update = st.toggle(
        "Update",
        value=update,
        key="boton_update",
        on_change=change_update
    )


# Mostrar número de documentos
st.subheader(f"Total de documentos guardados: {total_docs}")


# Añadir documentos y purgar base de datos
col1, col2 = st.columns(2)

with col1:
    nuevo_doc = st.text_input("ID del documento")
    if st.button("Añadir documento"):
        if nuevo_doc:
            añadir_documento(nuevo_doc)
        else:
            st.warning("Introduce un ID")

with col2:
    if st.button("Purgar base de datos"):
        purgar_bd()

st.divider()

# ------------------ Paginación ------------------

DOCS_POR_PAGINA = 5

if "pagina" not in st.session_state:
    st.session_state.pagina = 0

inicio = st.session_state.pagina * DOCS_POR_PAGINA
fin = inicio + DOCS_POR_PAGINA

docs_pagina = documentos[inicio:fin]

# ------------------ Mostrar documentos paginación ------------------

for doc in docs_pagina:
    doc_id = doc if isinstance(doc, str) else doc.get("id", "unknown")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(doc_id)

    with col2:
        if st.button("Eliminar", key=doc_id):
            eliminar_documento(doc_id)
            st.rerun()

# ------------------ Botones Paginación ------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("Anterior") and st.session_state.pagina > 0:
        st.session_state.pagina -= 1
        st.rerun()

with col2:
    if st.button("Siguiente") and fin < total_docs:
        st.session_state.pagina += 1
        st.rerun()