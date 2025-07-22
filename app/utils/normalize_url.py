from urllib.parse import urldefrag

def normalize_url(url: str) -> str:
    return urldefrag(url)[0]
