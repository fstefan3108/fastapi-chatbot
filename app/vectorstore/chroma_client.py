import chromadb
from chromadb.utils import embedding_functions
from app.api.deps import db_dependency
from app.models.website import Website

# initializes the persistent client which will keep data in the data directory after the functions runs; #
# sets the model for the embedding to all-mpnet-base-v2 (free model) #
# creates a new collection with embeddings that later gets stored in the persistent client. #

client = chromadb.PersistentClient(path="./data/vectordb")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

def embed_website_chunks(db: db_dependency, user_id: int):
    collection_name = f"user_{user_id}_collection"
    collection = client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_ef)
    chunks_list = []
    metadatas = []
    ids = []
    id = 1
    websites = db.query(Website).filter(Website.owner_id==user_id).all()
    for website in websites:
        for chunk in website.chunks:
            chunks_list.append(chunk)
            ids.append(str(id))
            metadatas.append({
                "owner_id": user_id,
                "website_id": website.id,
            })
            id += 1

    if chunks_list:
        collection.add(
            documents = chunks_list,
            metadatas = metadatas,
            ids = ids,
        )

