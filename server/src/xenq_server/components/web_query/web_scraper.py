import requests
from bs4 import BeautifulSoup
import re
import json

class WebsiteScraper:

    @staticmethod
    def scrape(url: str) -> str:
        """Fetch raw HTML content from the given URL."""
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to scrape {url}: {e}")
            return None

    @staticmethod
    def clean_html(raw_html: str) -> str:
        """Remove scripts/styles/nav etc. and extract plain visible text."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    @staticmethod
    def preprocess_text(cleaned_text: str) -> str:
        """Clean and normalize whitespace in the text."""
        text = re.sub(r'\s+', ' ', cleaned_text)
        return text.strip()

    @staticmethod
    def structure_content(raw_html: str) -> dict:
        """Extract structured info: title, meta, headings, paragraphs, lists."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        content = {
            "title": None,
            "meta_description": None,
            "headings": [],
            "paragraphs": [],
            "lists": [],
        }

        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text()

        meta_desc = soup.find('meta', attrs={"name": "description"})
        if meta_desc:
            content['meta_description'] = meta_desc.get('content', '')

        for level in range(1, 4):
            for h in soup.find_all(f'h{level}'):
                content['headings'].append({
                    "level": level,
                    "text": h.get_text(strip=True)
                })

        content['paragraphs'] = [p.get_text(strip=True) for p in soup.find_all('p')]

        for ul in soup.find_all('ul'):
            content['lists'].append({
                "type": "unordered",
                "items": [li.get_text(strip=True) for li in ul.find_all('li')]
            })

        for ol in soup.find_all('ol'):
            content['lists'].append({
                "type": "ordered",
                "items": [li.get_text(strip=True) for li in ol.find_all('li')]
            })

        return content

    @staticmethod
    def run_pipeline(url: str, structured: bool = False):
        """Run the full scraping and processing pipeline."""
        raw_html = WebsiteScraper.scrape(url)
        if not raw_html:
            return None, None

        cleaned = WebsiteScraper.clean_html(raw_html)
        preprocessed = WebsiteScraper.preprocess_text(cleaned)
        structured_content = WebsiteScraper.structure_content(raw_html) if structured else None

        return structured_content, preprocessed
