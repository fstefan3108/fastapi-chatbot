import re

def split_to_chunks(text: str, chunk_size: int = 5000) -> list[str]:
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Find end position #
        end = start + chunk_size

        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Adjusts the end of the chunk by respecting the ``` coming from a markdown #
        chunk = text[start:end]
        code_block = chunk.rfind('```')
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # Adjusts the end to happen at the end of the paragraph #
        elif '\n\n' in chunk:
            last_break = chunk.rfind("\n\n")
            if last_break > chunk_size * 0.3: # Breaks only if we are past 30% of the chunk size #
                end = start + last_break

        # If no paragraph, adjust the end to happen at the sentence, accounted for !, ., and ? #
        sentence_end_match = list(re.finditer(r"[.!?]\s", chunk))
        if sentence_end_match:
            last_end = sentence_end_match[-1].start()
            if last_end > chunk_size * 0.3:
                end = start + last_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, end)

    return chunks