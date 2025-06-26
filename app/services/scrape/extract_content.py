from bs4 import BeautifulSoup



### Parses the raw html into text with Beautiful Soup and returns the content of the <body></body>tag. ###

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""