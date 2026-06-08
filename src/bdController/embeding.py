from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def content_to_embedding(content: list[str]) -> list[list[float]]:
    """
    Convierte una lista de textos en embeddings usando SentenceTransformer.
    
    Args:
        content: lista de textos (cada chunk/documento)
    
    Returns:
        Lista de embeddings, cada embedding es una lista de floats
    """
    embeddings = model.encode(content, batch_size=32, show_progress_bar=True)
    return embeddings