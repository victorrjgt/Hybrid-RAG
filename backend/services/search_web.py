from tavily import TavilyClient
from backend.core.config import TAVILY_API_KEY

def buscar_en_internet(query: str) -> str:
    """
    Busca información en internet usando Tavily cuando el PDF no tiene la respuesta.
    Devuelve un texto con los fragmentos más relevantes encontrados en la web.
    """
    if not TAVILY_API_KEY:
        return "Error: No se ha configurado la API de Tavily."
        
    cliente = TavilyClient(api_key=TAVILY_API_KEY)
    resultados = cliente.search(query=query, search_depth="basic", max_results=3)
    
    # Extraer y juntar el contenido de las webs encontradas
    textos = [doc["content"] for doc in resultados.get("results", [])]
    return "\n\n".join(textos)