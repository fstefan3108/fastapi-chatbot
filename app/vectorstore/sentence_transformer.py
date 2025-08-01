from sentence_transformers import SentenceTransformer

_embedding_fn = None

def get_sentence_transformer():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_fn