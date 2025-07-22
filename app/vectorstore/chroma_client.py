from chromadb import PersistentClient
from chromadb.utils import embedding_functions

# Lazy loading the chroma client / Lazy Singleton #

_client = None
_embedding_fn = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = PersistentClient(path="./data/vectordb")
    return _client

def get_sentence_transformer():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_fn
