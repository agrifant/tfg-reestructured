import streamlit as st
import requests

# streamlit run front.py
# ------------------ VISTA 2: INFO ------------------

API_URL = "http://127.0.0.1:8002"

# ------------------ API CALLS ------------------
def obtener_documentos():
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

# ------------------ UI ------------------

st.title("Gestión de documentos")

documentos = obtener_documentos()
total_docs = len(documentos)

# 🔢 Número de documentos
st.subheader(f"Total de documentos: {total_docs}")

# 🔘 Botones superiores
col1, col2 = st.columns(2)

with col1:
    nuevo_doc = st.text_input("ID del documento")
    if st.button("➕ Añadir documento"):
        if nuevo_doc:
            añadir_documento(nuevo_doc)
        else:
            st.warning("Introduce un ID")

with col2:
    if st.button("🗑️ Purgar base de datos"):
        purgar_bd()

st.divider()

# ------------------ PAGINACIÓN ------------------

DOCS_POR_PAGINA = 5

if "pagina" not in st.session_state:
    st.session_state.pagina = 0

inicio = st.session_state.pagina * DOCS_POR_PAGINA
fin = inicio + DOCS_POR_PAGINA

docs_pagina = documentos[inicio:fin]

# ------------------ LISTA ------------------

for doc in docs_pagina:
    # 👇 ajusta esto según cómo venga tu JSON real
    doc_id = doc if isinstance(doc, str) else doc.get("id", "unknown")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(doc_id)

    with col2:
        if st.button("❌", key=doc_id):
            eliminar_documento(doc_id)
            st.rerun()

# ------------------ CONTROLES DE PAGINACIÓN ------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Anterior") and st.session_state.pagina > 0:
        st.session_state.pagina -= 1
        st.rerun()

with col2:
    if st.button("Siguiente ➡️") and fin < total_docs:
        st.session_state.pagina += 1
        st.rerun()