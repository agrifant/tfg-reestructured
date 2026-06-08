# streamlit run front.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8002"

st.title("RAG Legislativo")

# -------------------- Sección de Chat --------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

pregunta = st.chat_input("¿Qué quieres saber?")

if pregunta:
    st.session_state.mensajes.append(("user", pregunta))
    
    with st.spinner("Generando respuesta..."):
        try:
            response = requests.post(f"{API_URL}/preguntar", json={"query": pregunta})
            response.raise_for_status()
            respuesta = response.json().get("respuesta", "No hay respuesta")
        except requests.exceptions.RequestException as e:
            respuesta = f"Error al conectar con la API: {e}"
    
    st.session_state.mensajes.append(("assistant", respuesta))

# Mostrar historial de chat
for rol, mensaje in st.session_state.mensajes:
    with st.chat_message(rol):
        st.text(mensaje)