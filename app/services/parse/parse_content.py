from app.core.config import settings
import httpx

key = settings.api_key
url = settings.api_url


# Takes in context and user_prompt sent from the chatbot endpoint #
# Website content fetched by embedding is provided as context for the instructions #
# User content is the users prompt #
# Deepseek replies #

MAX_CONVOS = 3

async def parse_with_deepseek(context: list[str], history: list[dict]) -> str:
    history = history[-MAX_CONVOS*2:]
    full_context = "\n\n".join(context)
    messages = [
                   {
                       "role": "system",
                       "content": f"""
                        You are a helpful AI assistant that answers questions based only on the provided website content.

                        Your job is to help users understand what's available on the website, such as products, services, pricing, or company information.

                        Keep your responses clear, factual, and brief — ideally 2 to 4 sentences.
                        Do not explain your reasoning or show your thought process.
                        Do not include summaries or general information not found in the website content.

                        Website Content:
                        {full_context}
                        """
                  }
    ] + history

    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

    except httpx.RequestError as e:
        return f"Request failed: {e}"


    if response.status_code == 200:
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"No choices returned.\nFull response:\n{data}"
    else:
        return f"Error: {response.status_code}\n{response.text}"
