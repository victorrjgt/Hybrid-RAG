from langchain_google_genai import ChatGoogleGenerativeAI
from backend.core.vector_store import get_vector_store
from backend.services.search_web import buscar_en_internet

# Inicializamos a Gemini
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)

# Añadimos un parámetro para que el usuario decida si permite usar internet
def responder_pregunta(pregunta: str, permitir_busqueda_web: bool = True) -> dict:
    """
    Flujo de Corrective RAG:
    1. Busca en el PDF.
    2. Evalúa si la información sirve.
    3. Si no sirve y el usuario dio permiso, busca en internet.
    """
    # Buscar en el PDF (ChromaDB)
    vector_store = get_vector_store()
    docs_pdf = vector_store.similarity_search(pregunta, k=4)
    texto_pdf = "\n\n".join([doc.page_content for doc in docs_pdf])
    
    # Prompt para evaluar
    prompt_evaluador = f"""
    Eres un evaluador estricto. Tu tarea es decirme si el siguiente TEXTO contiene información 
    útil para responder a la PREGUNTA.
    Solo puedes responder con la palabra "SI" o "NO". No expliques nada más.
    
    PREGUNTA: {pregunta}
    TEXTO: {texto_pdf}
    """
    
    response = llm.invoke(prompt_evaluador)
    
    # Extracción segura
    contenido = response.content
    texto_evaluacion = ""
    if isinstance(contenido, str):
        texto_evaluacion = contenido
    elif isinstance(contenido, list) and len(contenido) > 0:
        primer_elemento = contenido[0]
        if isinstance(primer_elemento, dict) and "text" in primer_elemento:
            texto_evaluacion = primer_elemento["text"]
        else:
            texto_evaluacion = str(primer_elemento)
    else:
        texto_evaluacion = str(contenido)
        
    respuesta_evaluacion = texto_evaluacion.strip().upper()
    
    # Redacción
    fuente_usada = "PDF Local"
    contexto_final = texto_pdf
    
    # Si el PDF NO tiene la respuesta
    if "NO" in respuesta_evaluacion or not texto_pdf:
        # Comprobamos si el usuario nos dio permiso para ir a internet
        if permitir_busqueda_web:
            print("El PDF no tiene la respuesta. Activando búsqueda web permitida...")
            fuente_usada = "Internet (Tavily)"
            contexto_final = buscar_en_internet(pregunta)
        else:
            print("El PDF no tiene la respuesta y la búsqueda web está desactivada.")
            # Si no hay permiso, cortamos aquí y avisamos al usuario
            return {
                "respuesta": "Lo siento, la respuesta no se encuentra en el documento proporcionado y la búsqueda en internet está desactivada.",
                "fuente": "Sin respuesta"
            }
    else:
        print("Información encontrada en el PDF.")
        
    # Respuesta Final
    prompt_final = f"""
    Responde a la pregunta del usuario basándote ÚNICAMENTE en el siguiente contexto.
    Si la respuesta no está en el contexto, di que no lo sabes.
    Sé claro y usa formato Markdown.
    
    PREGUNTA: {pregunta}
    CONTEXTO: {contexto_final}
    """
    
    respuesta_final = llm.invoke(prompt_final).content
    
    # Extracción final
    texto_limpio_final = ""
    if isinstance(respuesta_final, str):
        texto_limpio_final = respuesta_final
    elif isinstance(respuesta_final, list) and len(respuesta_final) > 0:
        primer_elemento_final = respuesta_final[0]
        if isinstance(primer_elemento_final, dict) and "text" in primer_elemento_final:
            texto_limpio_final = primer_elemento_final["text"]
        else:
            texto_limpio_final = str(primer_elemento_final)
    else:
        texto_limpio_final = str(respuesta_final)
    
    return {
        "respuesta": texto_limpio_final,
        "fuente": fuente_usada
    }