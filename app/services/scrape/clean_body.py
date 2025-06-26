from bs4 import BeautifulSoup



### Removes <style> and <script> tags, removes blank spaces and adds new lines accordingly. ###

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, 'html.parser')

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator='\n')
    cleaned_content = '\n'.join(line.strip() for line in cleaned_content.splitlines() if line.strip())

    return cleaned_content