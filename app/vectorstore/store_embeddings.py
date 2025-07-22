from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_website import crud_website
from app.models.website import Website
from app.utils.split_chunks import split_to_chunks
from app.vectorstore.chroma_client import get_chroma_client, get_sentence_transformer

# initializes the persistent client which will keep data in the data directory after the functions runs; #
# sets the model for the embedding to all-mpnet-base-v2 (free model) #
# creates a new collection with embeddings that later gets stored in the persistent client. #

async def store_embedding_data(db: AsyncSession, user_id: int):
    client = get_chroma_client()
    sentence_transformer_ef = get_sentence_transformer()

    criteria = Website.owner_id == user_id
    websites = await crud_website.get_by(db=db, criteria=criteria)

    for website in websites:

        collection_name = f"user_{user_id}_website_{website.id}"
        collection = client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_ef)

        chunks_list = []
        metadatas = []
        ids = []
        id = 1

        for markdown in website.markdown:
            chunks = split_to_chunks(markdown)

            for chunk in chunks:

                chunks_list.append(chunk)
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


