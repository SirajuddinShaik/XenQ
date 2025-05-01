# __init__.py for agent/src/xenq_agent/components/web_query/__init__.py

import json

from xenq_server.api import AioHTTPSessionManager
from xenq_server.config import AGENT_URI
from .search_engine import DuckDuckGoSearch
from .summarizer import Summarizer
from .web_scraper import WebsiteScraper
import chainlit as cl
import asyncio


class WebQuery:
    def __init__(self):
        self.search_engine = DuckDuckGoSearch()
        self.summarizer = Summarizer()
        self.scraper = WebsiteScraper()

    
    def process_urls(self, urls):
        token_cnt = 0
        for url in urls:
            if token_cnt < 5000:
                content = self.scraper.run_pipeline(url["href"])
                content_words = content.split()  # split into words
                
                if token_cnt + len(content_words) > 5000:
                    # Trim words so total token count remains within 5000
                    allowed_words = 5000 - token_cnt
                    content_words = content_words[:allowed_words]
                
                content = " ".join(content_words)  # join back trimmed words
                token_cnt += len(content_words)  # update token count based on number of words
                url["scraped_content"] = content
            else:
                break

        return urls

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

    def build_prompt(self, query, urls) -> str:
        prompt = web_sys_prompt.format(query = query, json_context = str(urls))
        return prompt

    async def search_web(self, query, top_k=4):
        urls = self.search_engine.search_top_url(query, top_k)
        extraced_urls = self.process_urls(urls)
        prompt = self.build_prompt(query = query, urls = urls)
        
        session = await AioHTTPSessionManager.get_session()
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        response=""
        msg = cl.Message(content = "", author="web_whisper")
        try:
            async with session.post(f"{AGENT_URI}/stream", headers=headers, json={"prompt": prompt}) as resp:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data:"):
                        try:
                            data = json.loads(decoded[5:])
                            token = data.get("token", "")
                            response += token
                            await msg.stream_token(token)

                        except Exception as e:
                            print("Streaming error:", e)
        except Exception as e:
            print("Request failed:", e)
        await msg.update()  
        return {"role": "web_whisper", "content": response}



web_sys_prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

🕸️ Web Scraping Summarization Assistant

The user has already provided their query, and the system has gathered relevant web content for you.

You are now responsible for:
- Carefully reading the provided **User Query**:  
  > {query}
- And the **Scraped Web Content (JSON format)**: Each entry typically includes a `title`, `href` (URL), `body` (text) and `scraped_content` (text). 
```json
{json_context}
```
🎯 Your task:
- **Summarize and explain** the important parts of the scraped content **directly addressing the user's query**.
- **Talk naturally and intelligently** to the user — keep it clear, smart, and conversational.
- Make your reply feel like you're helping a real person, not just dumping a summary.

Important rules:
- 📚 Use only the given content — **no outside information or assumptions**.
- 🔍 Focus on answering the **User Query** using the available context.
- ✂️ If the content doesn't fully answer the query, explain what you found and mention politely if some information was missing.
- 🧠 Think carefully before you answer. Stay focused on being helpful and relevant.

How to structure your answer:
1. 🎯 **Quick Direct Answer** (react to the query in 1-2 lines)
2. 📚 **Organized Summary** based on the scraped content
3. 🧩 (Optional) Mention any source titles if it makes the explanation clearer

---

Now go ahead and respond thoughtfully to the user based on the available content! 🚀

<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""