# search_engine.py for agent/src/xenq_agent/components/web_query/search_engine.py
import requests
from bs4 import BeautifulSoup

from duckduckgo_search import DDGS

class DuckDuckGoSearch:
    def __init__(self):
        self.search_engine = DDGS()

    def search_top_url(self, query: str, max_results = 4) -> list[dict[str, str]]:
        results = list(self.search_engine.text(query, max_results=max_results))
        if results:
            return results
        return [{}]
