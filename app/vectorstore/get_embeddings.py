from app.vectorstore.store_embeddings import client

# Gets passed the prompt, user's id and website's id when the endpoint is called #
# Fetches the collection with the dynamicaly set name for each user #
# Queries through the collection by user_prompt, returns 10 best matches for the provided prompt, #
# which are stored in the collection after scraping the website. Returns the website content which #
# best matches the prompt and gives it to deepseek. #

def get_embeddings(user_id: int, user_prompt: str, website_id: int):
    collection = client.get_collection(name=f"user_{user_id}_collection")

    results = collection.query(
        query_texts=user_prompt,
        n_results=10,
        where={"website_id": website_id},
        include=["documents"]
    )


    return results["documents"]