import streamlit as st
import requests

# ------------------ VISTA 2: INFO ------------------

API_URL = "http://127.0.0.1:8002"

# ------------------ API CALLS ------------------
def obtener_documentos(page):
    #
    #Devuleve una lista con los nombres y el número de documentos insertados
    if page==1:
        return ["Boe-1", "Boe-2", "Boe-3"], 11, 3
    else:
        return ["Boe-3", "Boe-4", "Boe-5"], 11, 3

    """
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
    """


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

def delete_doc(id):
    print(f"Eliminando doc {id}")


# ------------------ UI ------------------
st.title("Gestión de documentos")

if "pagina" not in st.session_state:
    st.session_state.pagina = 1
    
documentos, total_docs, max_pages = obtener_documentos(st.session_state.pagina)


# Mostrar número de documentos
st.subheader(f"Total de documentos guardados: {total_docs}")

st.divider()


# Obtener el estado inicial desde una función
delete, update = obtener_estado()


# Botones de los mecanismos delete, unificate y purgar
col1, col2, col3 = st.columns(3)

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


with col3:
    if st.button("Purgar base de datos"):
            purgar_bd()


# Añadir documento
st.subheader(f"Agregar nuevo documento")
nuevo_doc = st.text_input("ID del documento a añadir")

if st.button("Añadir documento"):
            if nuevo_doc:
                añadir_documento(nuevo_doc)
            else:
                st.warning("Introduce un ID")

st.subheader(f"Eliminar documento")
del_doc = st.text_input("ID del documento a eliminar")

if st.button("Eliminar documento"):
            if del_doc:
                delete_doc(del_doc)
            else:
                st.warning("Introduce un ID")

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
            eliminar_documento(doc_id)
            st.rerun()

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