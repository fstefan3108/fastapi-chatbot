from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_to_chunks(text: str) -> list[str]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=0,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_text(text)
    return chunks