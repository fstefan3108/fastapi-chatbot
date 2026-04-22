from sentence_transformers import SentenceTransformer

_embedding_fn = None

def get_sentence_transformer():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformer("tomaarsen/static-similarity-mrl-multilingual-v1", trust_remote_code=True)
    return _embedding_fn