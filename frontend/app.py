import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="RAG Híbrido Avanzado", page_icon="💾🌐", layout="wide")

# URL base de nuestra API (FastAPI)
API_URL = "http://localhost:8000"

st.title("RAG Híbrido: Documentos + Web")
st.markdown("""
Este sistema busca primero en tus documentos locales. Si no encuentra la respuesta, 
te pedirá permiso para buscar en internet.
""")

# Inicializar el historial de chat en la sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- BARRA LATERAL (SUBIDA Y CONFIGURACIÓN) ---
with st.sidebar:
    st.header("Configuración")
    
    # Interruptor Human-in-the-Loop (HITL)
    permitir_web = st.toggle(
        "Permitir búsqueda web", 
        value=True, 
        help="Si se activa, buscará en internet cuando el PDF no tenga la respuesta."
    )
    
    st.divider()
    
    # Subida de PDF
    st.header("Tus Documentos")
    archivo_pdf = st.file_uploader("Sube un archivo PDF", type=["pdf"])
    
    if st.button("Procesar PDF", type="primary", use_container_width=True):
        if archivo_pdf is not None:
            with st.spinner("Procesando documento..."):
                try:
                    # Preparamos el archivo para enviarlo a FastAPI
                    archivos = {"file": (archivo_pdf.name, archivo_pdf.getvalue(), "application/pdf")}
                    respuesta = requests.post(f"{API_URL}/upload-pdf", files=archivos)
                    
                    if respuesta.status_code == 200:
                        datos = respuesta.json()
                        st.success(f"¡Listo! {datos['fragmentos_creados']} documento indexado.")
                    else:
                        st.error(f"Error: {respuesta.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Error de conexión: ¿Está el servidor FastAPI encendido?")
        else:
            st.warning("Selecciona un PDF primero.")


# --- ZONA PRINCIPAL (CHAT) ---
# Mostrar el historial de mensajes
for msg in st.session_state.mensajes:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["contenido"])
        if "fuente" in msg:
            st.caption(f"Fuente: {msg['fuente']}")

# Caja de texto para el usuario
if prompt := st.chat_input("Pregunta algo sobre el documento..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
    
    # Consultar a la API
    with st.chat_message("assistant"):
        with st.spinner("Pensando y evaluando fuentes..."):
            try:
                payload = {
                    "pregunta": prompt,
                    "permitir_busqueda_web": permitir_web
                }
                respuesta = requests.post(f"{API_URL}/chat", json=payload)
                
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    texto_respuesta = datos["respuesta"]
                    fuente = datos["fuente"]
                    
                    st.markdown(texto_respuesta)
                    st.caption(f"Fuente: {fuente}")
                    
                    # Guardar en historial
                    st.session_state.mensajes.append({
                        "rol": "assistant", 
                        "contenido": texto_respuesta,
                        "fuente": fuente
                    })
                else:
                    st.error(f"Error en la API: {respuesta.text}")
            except requests.exceptions.ConnectionError:
                st.error("Error de conexión: Asegúrate de encender FastAPI en la otra terminal.")