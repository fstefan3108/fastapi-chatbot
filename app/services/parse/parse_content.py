from app.core.config import settings
import httpx

key = settings.api_key
url = settings.api_url


# Takes in context and user_prompt sent from the chatbot endpoint #
# Website content fetched by embedding is provided as context for the instructions #
# User content is the users prompt #
# Deepseek replies #

async def parse_with_deepseek(context: str, history: list[dict], current_prompt: str) -> str:
    # adds only last three conversations #
    messages = [
                   {
                       "role": "system",
                       "content": f"""
You are a helpful AI assistant that answers questions based only on the provided website content.

Your job is to help users understand what's available on the website, such as products, services, pricing, or company information.

IMPORTANT RULES:
- Do NOT include any internal thoughts or monologues.
- NEVER use <think> tags or describe your reasoning.
- Only give direct, concise answers based on the provided content.
- If the answer is not found, say: "That information is not available on the website."

Website Content:
{context}
"""
        },
        *history,
        {
            "role": "user",
            "content": current_prompt
        }
    ]

    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
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
        try:
            data = response.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                return f"No choices returned.\nFull response:\n{data}"
        except Exception as e:
            return f"Failed to parse response JSON: {e}"
    else:
        return f"Error: {response.status_code}\n{response.text}"