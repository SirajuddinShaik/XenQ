# history_store.py for agent/src/xenq_agent/components/query/history_store.py
from datetime import datetime
from zoneinfo import ZoneInfo

from xenq_server.utils.sys_p import p8, p9
from xenq_server.utils.qwen_sys import qwen
default_system_msg = "Your next-gen AI assistant, built to understand, generate, and evolve with every query. Ask smart. Get smarter."
default_system_msg = p9
class HistoryStore:
    def __init__(self, system_msg = default_system_msg):
        self.system_msg = {"msg": system_msg, "cum_word_len": len(system_msg.split())}
        self.max_words = 5000
        self.history = []
        self.memory = []
        self.tmp_resoning = ""
    
    def append_content(self, role: str, content: str = ""):
        prev_cum_len = self.history[-1]["cum_word_len"] if self.history else 0
        length = len(content.split())
        if length < 800 or role == "backend":
            cum_word_len = prev_cum_len + length
            self.history.append({
                "role": role,
                "content": content,
                "cum_word_len": cum_word_len
            })
            return True
        else:
            return False

    def add_reasoning(self, content):
        self.tmp_resoning += content

    def append_reasoning(self, content):
        self.append_content("assistant", self.tmp_resoning + content)
        self.tmp_resoning = ""
        
    def update_system_msg(self, msg):
        if msg:
            self.system_msg = {"msg": msg, "cum_word_len": len(msg.split())}
        else:
            self.system_msg = {"msg": default_system_msg, "cum_word_len": len(msg.split())}

    def build_prompt(self):
        # Start with the system message
        memo = '\n- '.join(self.memory)
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        formatted = f"🕒 The exact current date and time (India Standard Time) at this moment is: {now.strftime('%A, %B %d, %Y at %I:%M %p')}(IST).use this for time related queries"
        system = self.system_msg["msg"].replace("{memory}", memo if memo else "").replace("{date_time}", formatted) 
        prompt = self.templates["system"].format(content=system)

        # Determine the starting index of history to include within max_words constraint
        start_idx = 0
        for idx in range(len(self.history)):
            total_words = (
                self.history[-1]["cum_word_len"] 
                - self.history[idx]["cum_word_len"] 
                + self.system_msg["cum_word_len"]
            )
            if total_words <= self.max_words:
                start_idx = idx
                break

        # Add messages from the determined start index
        for msg in self.history[start_idx:]:
            prompt += self.templates[msg["role"]].format(content=msg["content"])
        prompt+=self.tmp_resoning
        return prompt


    templates = {
        "system": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>{content}<|eot_id|>",
        "user": "<|start_header_id|>user<|end_header_id|>{content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "assistant": "{content}",
        "memory": "### Memory\n- {content.join('\n- ')}",
        "table": "#### Query: {query}\nOutput:\n{table}",
        "light_rag": "</internal><|eot_id|><|start_header_id|>rag<|end_header_id|>\n{content}<|eot_id|>",
        "web_whisper": "</internal><|eot_id|><|start_header_id|>WebWhisper<|end_header_id|>\n{content}<|eot_id|>",
        "database_query": "</internal><|start_header_id|>backend<|end_header_id|>\n{content}\n\n- If the backend fails, retry 2–3 times; since internal blocks are hidden, explain the result naturally as if you figured it out, and if all retries fail, inform the user with a clear, friendly explanation of the error.<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "web_query": "",
        "client": "</internal><|eot_id|><|start_header_id|>remote_controller<|end_header_id|>\n{content}<|eot_id|>"
    }
    templates1 = {
    "system": "<|im_start|>system\n{content}<|im_end|>\n",
    "user": "<|im_start|>user\n{content}<|im_end|>\n<|im_start|>assistant\n",
    "assistant": "{content}<|im_end|>\n",
    "memory": "### Memory\n- {content.join('\\n- ')}",
    "table": "#### Query: {query}\nOutput:\n{table}",
    "light_rag": "<|im_start|>rag\n{content}<|im_end|>\n",
    "web_whisper": "<|im_start|>WebWhisper\n{content}<|im_end|>\n",
    "backend": "<|im_start|>backend\n{content}\n\n- If the backend fails, retry 2–3 times; since internal blocks are hidden, explain the result naturally as if you figured it out, and if all retries fail, inform the user with a clear, friendly explanation of the error.<|im_end|>\n<|im_start|>assistant\n",
    "web_query": "",  # You can define this based on your web module structure
    "client": "<|im_start|>remote_controller\n{content}<|im_end|>\n"
}
