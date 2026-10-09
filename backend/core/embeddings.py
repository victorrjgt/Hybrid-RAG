from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function() -> HuggingFaceEmbeddings:
    """
    Retorna el modelo de embeddings de HuggingFace.
    Usamos 'sentence-transformers/all-MiniLM-L6-v2' por ser un estándar de la industria:
    es gratuito, corre 100% en local en la CPU y genera vectores de 384 dimensiones.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings