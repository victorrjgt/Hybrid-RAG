from langchain_chroma import Chroma
from backend.core.config import CHROMA_PATH
from backend.core.embeddings import get_embedding_function

def get_vector_store() -> Chroma:
    """
    Inicializa y devuelve la conexión a la base de datos local ChromaDB.
    """
    embeddings = get_embedding_function()
    vector_store = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embeddings
    )
    return vector_store