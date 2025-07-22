import asyncio
from app.core.logger import logger
from app.vectorstore.chroma_client import get_chroma_client

# Gets passed the prompt, user's id and website's id when the endpoint is called #
# Fetches the collection with the dynamicaly set name for each user #
# Queries through the collection by user_prompt, returns 10 best matches for the provided prompt, #
# which are stored in the collection after scraping the website. Returns the website content which #
# best matches the prompt and gives it to deepseek. #


async def get_embeddings(user_id: int, user_prompt: str, website_id: int) -> list[str]:
    client = get_chroma_client()
    collection = client.get_collection(name=f"user_{user_id}_website_{website_id}")

    try:
        results = await asyncio.to_thread(
            collection.query,
            query_texts=[user_prompt],
            n_results=5,
            include=["documents", "distances"]
        )

        return results.get("documents", [])

    except Exception as e:
        logger.error(f"Error querying embeddings: {e}")
        return []


