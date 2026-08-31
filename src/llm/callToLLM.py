import requests
from ollama import chat
import os
import time

#Variables globales para que tenga memoria
max_memory_turns=3
history_text=[]

#Hacer pregunta a ollama
def call_ollama(messages, format=None, num_predict=-1):
    """
    Función genérica que realiza la llamada al llm ollama

    Inputs:
        messages: list[dict]. Recibe el mensaje con el role de system y user
        [{"role": "system", "content": ...},
        {"role": "user", "content": ...},
        ...]

    outputs:
        string: La respuesta del llm
    """
    params = {
        "model": "llama3.1:8b",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0,
        "num_predict": num_predict
        }
    }

    if format:
        params["format"] = format

    response = chat(**params)
    
    return response["message"]["content"].strip()

#Funciones relacionadas con las preguntas del rag
def addToHistory(query, response):
    # Cada turno tiene 2 entradas: pregunta + respuesta
    for item in [f"Usuario: {query}", f"Asistente: {response}"]:
        if len(history_text) >= 2 * max_memory_turns:
            history_text.pop(0)  # eliminar lo más antiguo
        history_text.append(item)

def writeHistory():
    return "\n".join(history_text)

def pront_ask_rag(contexto_completo, query, history_text):

    system_prompt = """Eres un asistente jurídico especializado en análisis de textos legales.
        TU OBJETIVO:
        Responder preguntas jurídicas utilizando EXCLUSIVAMENTE la información contenida en el CONTEXTO JURÍDICO proporcionado.
        
        ========================
        REGLAS FUNDAMENTALES
        ========================
        1. Prohibido absoluto: usar conocimiento externo, general o previo.
        2. Prohibido inferir normas no escritas explícitamente en el contexto.
        3. Prohibido completar lagunas con lógica jurídica o sentido común.
        4. Cada afirmación debe estar respaldada por al menos un fragmento del CONTEXTO.
        5. Si la información no está explícita en el contexto:
           - responde exactamente: "No tengo suficiente información, lo siento."
        
        ========================
        REGLA CLAVE
        ========================
        Antes de responder:
        - Identifica qué Documento(s) del CONTEXTO contienen la respuesta.
        - Si ningún documento contiene la respuesta de forma directa → no respondas.
        
        NO está permitido:
        - Mezclar documentos sin indicarlo
        - Interpretar artículos más allá de su texto literal
        - Resumir sin base textual clara
        
        ========================
        REGLAS DE RESPUESTA
        ========================
        - Usa estilo jurídico formal, pero literal.
        - Prioriza citas textuales cuando sea posible.
        - No reformules el contenido si no es necesario.
        - Si citas, indica claramente: "Documento X: ..."
        
        ========================
        FORMATO OBLIGATORIO
        ========================
        1. Respuesta breve y directa.
        2. Cita del/los documento(s) utilizados.
        3. Si no hay evidencia explícita → mensaje estándar de insuficiencia.
        
        NO incluyas explicaciones sobre estas instrucciones.
        """
    
    user_prompt = f"""HISTORIAL:
        {history_text}
        
        CONTEXTO JURÍDICO:
        {contexto_completo}
        
        PREGUNTA:
        {query}
        
        INSTRUCCIÓN CRÍTICA:
        Primero identifica si existe evidencia explícita en el contexto. Solo responde si puedes citarla literalmente.
        """

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def make_rag_question(query: str, chunks):
    global history_text
    contexto_completo="\n\n".join(chunks)
    #Escribirmos el promt
    prompt=pront_ask_rag(contexto_completo, query, history_text)

    response=call_ollama(prompt, None, 300)
    
    addToHistory(query, response)
    return response
