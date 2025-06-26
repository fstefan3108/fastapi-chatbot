import requests
import json
from app.core.config import settings

key = settings.api_key
url = settings.api_url


# Takes in context and user_prompt sent from the chatbot endpoint #
# Website content fetched by embedding is provided as context for the instructions #
# User content is the users prompt #
# Deepseek replies #


def parse_with_deepseek(context: list[str], user_prompt: str):

    messages = [
        {
            "role": "system",
            "content": f"You are an assistant that answers questions based on website content. \n\nWebsite Content: {context}"
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    response = requests.post(
        url=url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": messages,
        })
    )

    print("Response status:", response.status_code)
    print("Response text:", response.text)

    if response.status_code == 200:
        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            return reply
        else:
            return f"ENo choices returned. Full response: {json.dumps(data, indent=2)}"
    else:
        return f"Error: {response.status_code}\n{response.text}"