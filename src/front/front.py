# streamlit run front.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8002"

st.title("RAG Legislativo")
st.sidebar.header("Configuración")

# ------------------ API CALLS ------------------
def get_umbral():
    #Añadir api del backend
    try:
        threshold = requests.get(
            f"{API_URL}/mecanismoThreshold"
        )

        if threshold.status_code == 200:
            value=threshold.json()
        else:
            value=0


        return value
    
    except Exception:
        st.error("Error de conexión")
    return 0


def update_umbral():
    valor = st.session_state["umbral"]
    
    try:
        requests.post(
            f"{API_URL}/mecanismoThreshold",
            json={"value":valor})

    except Exception:
        st.session_state["umbral"] = 0.0
        st.error("Error de conexión")
    

def get_rag_response(pregunta):
    try:
        response = requests.post(f"{API_URL}/preguntar", json={"query": pregunta})

        return response.json().get("respuesta", "Error generando la resupesta. Disculpen las molestias")
    except Exception:
        return "Error generando la resupesta. Disculpen las molestias"


# -------------------- Configuración del umbral --------------------

# Obtener el umbral actual del backend
if "umbral" not in st.session_state:
    st.session_state.umbral = get_umbral()


# barra elección umbral
st.sidebar.slider(
    "Umbral de similitud",
    min_value=0.0,
    max_value=1.0,
    step=0.05,
    key="umbral",
    on_change=update_umbral,
    help=(
        "Configura el parámetro Similarity Threshold Filtering. "
        "Para desactivar el filtrado, establece el umbral en 0."
    )
)


# -------------------- Sección de Chat --------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

pregunta = st.chat_input("¿Qué quieres saber?")

if pregunta:
    st.session_state.mensajes.append(("user", pregunta))
    
    with st.spinner("Generando respuesta..."):
        respuesta=get_rag_response(pregunta)
    
    st.session_state.mensajes.append(("assistant", respuesta))


# -------------------- Historial --------------------
for rol, mensaje in st.session_state.mensajes:
    with st.chat_message(rol):
        st.text(mensaje)