from sqlalchemy.orm import Session
from app.crud.crud_website import crud_website
from app.models.website import Website
from app.vectorstore.chroma_client import get_chroma_client, get_sentence_transformer
from app.core.logger import logger
from app.vectorstore.text_cleaner import TextCleaner


# initializes the persistent client which will keep data in the data directory after the functions runs; #
# sets the model for the embedding to all-mpnet-base-v2 (free model) #
# creates a new collection with embeddings that later gets stored in the persistent client. #

def store_embedding_data(db: Session, user_id: int):
    cleaner = TextCleaner()
    client = get_chroma_client()
    sentence_transformer_ef = get_sentence_transformer()

    criteria = Website.owner_id == user_id
    websites = crud_website.get_by_sync(db=db, criteria=criteria)

    for website in websites:

        collection_name = f"user_{user_id}_website_{website.id}"
        collection = client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_ef)

        chunks_list = []
        metadatas = []
        ids = []
        id = 1

        logger.info(type(website.chunks))
        for chunk in website.chunks:

            logger.info(f"Uncleaned chunk:{chunk}")
            cleaned_chunk = cleaner.clean(chunk)
            logger.info(f"Cleaned chunk:{cleaned_chunk}")

            chunks_list.append(cleaned_chunk)
            ids.append(str(id))
            metadatas.append({
                "owner_id": user_id,
                "website_id": website.id,
            })
            id += 1

        if chunks_list:
            collection.add(
                documents=chunks_list,
                metadatas=metadatas,
                ids=ids,
            )


