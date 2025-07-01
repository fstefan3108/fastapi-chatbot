from app.api.deps import db_dependency, user_dependency
from app.crud.crud_chat import add_user_prompt, add_deepseek_reply, get_chat_history
from app.schemas.chat import ChatRequest
from app.services.parse.format_chat import format_chat_history
from app.services.parse.parse_content import parse_with_deepseek
from app.utils.db_transaction import db_transactional
from app.vectorstore.get_embeddings import get_embeddings


@db_transactional
def handle_chat(db: db_dependency, user: user_dependency, chat: ChatRequest):
    add_user_prompt(db=db, chat=chat, user=user)

    context = get_embeddings(user_id=user.get("id"), user_prompt=chat.message, website_id=chat.website_id)
    print("💡 Retrieved Context:", context)

    chat_history = get_chat_history(db=db, chat=chat)
    formatted_history = format_chat_history(chat_history)

    deepseek_reply = parse_with_deepseek(context=context, history=formatted_history)

    add_deepseek_reply(db=db, chat=chat, user=user, reply=deepseek_reply)

    return deepseek_reply