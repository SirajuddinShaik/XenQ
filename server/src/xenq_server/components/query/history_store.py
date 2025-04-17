# history_store.py for agent/src/xenq_agent/components/query/history_store.py

from xenq_server.utils.sys_p import p1, p2, p4, p3
default_system_msg = "Your next-gen AI assistant, built to understand, generate, and evolve with every query. Ask smart. Get smarter."
default_system_msg = p4
class HistoryStore:
    def __init__(self, system_msg = default_system_msg):
        self.system_msg = {"msg": system_msg, "cum_word_len": len(system_msg.split())}
        self.max_words = 4000
        self.history = []
        self.tmp_resoning = ""
    
    def append_content(self, role, content):
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
        prompt = self.templates["system"].format(content=self.system_msg["msg"])

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
        "backend": "<|start_header_id|>backend<|end_header_id|>\n{content}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "web_query": ""
    }