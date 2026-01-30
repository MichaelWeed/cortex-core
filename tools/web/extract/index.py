import requests
from bs4 import BeautifulSoup
import html2text

def main(url):
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "SovereignIndexer/1.0"})
        response.raise_for_status()
        
        # Convert HTML to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        markdown = h.handle(response.text)
        
        # Basic metadata
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        
        return {
            "title": title,
            "markdown": markdown[:5000], # Cap to 5000 chars for LLM context
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}
