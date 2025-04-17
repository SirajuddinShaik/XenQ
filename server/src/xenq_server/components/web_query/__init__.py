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

    def convert_to_markdown(self, data):
        markdown_output = "\n"

        for item in data:
            title = item.get("title", "No Title")
            href = item.get("href", "#")
            body = item.get("body", "")
            processed = item.get("processed", [])

            # Title and Link
            markdown_output += f"#### 🔹 [{title}]({href})\n"

            # # Body
            # body_lines = body.strip().split(". ")
            # for line in body_lines:
            #     markdown_output += f"> {line.strip()}\n"
            markdown_output += f"\n> {body}"

            # Processed Notes
            if processed:
                markdown_output += "💡 **Processed Notes**:\n"
                for note in processed:
                    if len(processed) == 1:
                        markdown_output += f"`{note}`\n"
                    else:
                        markdown_output += f"- {note.strip()}\n"

            markdown_output += "\n\n"

        return markdown_output.strip()

    async def search_web(self, query, top_k=2):
        urls = self.search_engine.search_top_url(query, top_k)

        async def process_url(url):
            try:
                processed_text = self.scraper.run_pipeline(url["href"])[1]
                summarized_text = await self.summarizer.summarize_text(processed_text, query)
                url["processed"] = summarized_text
            except Exception as e:
                url["processed"] = ["No Data Available!"]

        tasks = [process_url(url) for url in urls]
        await asyncio.gather(*tasks)
        output = self.convert_to_markdown(urls)
        return output


    
        