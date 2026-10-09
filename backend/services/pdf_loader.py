from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.core.vector_store import get_vector_store

def procesar_y_guardar_pdf(ruta_pdf: str) -> int:
    """
    Lee un PDF, lo divide en fragmentos (chunks) y los guarda en ChromaDB.
    Devuelve el número de fragmentos generados.
    """
    # 1. Leer el PDF completo
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()

    # 2. Triturador inteligente de texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # Cada trozo tendrá máximo 1000 caracteres
        chunk_overlap=200, # Solapamos 200 caracteres para no cortar ideas o frases a medias
        separators=["\n\n", "\n", ".", " ", ""]
    )
    fragmentos = text_splitter.split_documents(documentos)

    # 3. Enviar los fragmentos a la base de datos vectorial
    vector_store = get_vector_store()
    vector_store.add_documents(fragmentos)
    
    return len(fragmentos)