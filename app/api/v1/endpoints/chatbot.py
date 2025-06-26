from fastapi import APIRouter, Body

from app.api.deps import user_dependency
from app.core.security import check_user
from app.services.parse.parse_content import parse_with_deepseek
from app.vectorstore.get_embeddings import get_embeddings

router = APIRouter()

@router.post("/prompt/{website_id}", status_code=201)
async def index(user: user_dependency, website_id: int, prompt: str = Body(...)):
    check_user(user)

    context = get_embeddings(user_id=user.get("id"), user_prompt=prompt, website_id=website_id)
    deepseeks_response = parse_with_deepseek(context=context, user_prompt=prompt)

    return {"response": deepseeks_response}
