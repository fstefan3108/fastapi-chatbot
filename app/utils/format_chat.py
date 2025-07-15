def format_chat_history(chat_history):
    return [
        {"role": chat.get("role") if isinstance(chat, dict) else chat.role,
         "content": chat.get("content") if isinstance(chat, dict) else chat.message}
        for chat in chat_history
    ]