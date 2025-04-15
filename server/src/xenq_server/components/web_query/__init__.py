# __init__.py for agent/src/xenq_agent/components/web_query/__init__.py

from .search_engine import DuckDuckGoSearch
from .summarizer import Summarizer
from .web_scraper import WebsiteScraper
import asyncio


class WebQuery:
    def __init__(self):
        self.search_engine = DuckDuckGoSearch()
        self.summarizer = Summarizer()
        self.scraper = WebsiteScraper()

    async def search_web(self, query, top_k=2):
        urls = self.search_engine.search_top_url(query, top_k)

        async def process_url(url):
            processed_text = self.scraper.run_pipeline(url["href"])[1]
            summarized_text = await self.summarizer.summarize_text(processed_text, query)
            url["processed"] = summarized_text

        tasks = [process_url(url) for url in urls]
        await asyncio.gather(*tasks)
        return urls


    
        