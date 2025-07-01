def format_chat_history(chat_history):
    return [
        {"role": chat.role, "content": chat.message}
        for chat in chat_history
    ]