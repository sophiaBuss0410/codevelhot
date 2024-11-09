from helpers import singleton, generator_simulator

import openai
from dotenv import load_dotenv
import os


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
tools_list = []

@singleton
class OpenAIClient:
    def __init__(self, **kwargs):
        self.vllms_api = kwargs.get("vllms_api", None)
        self.client = openai.Client(base_url= self.vllms_api ,api_key=OPENAI_API_KEY)
        self.model = kwargs.get("model_name")
        self.temperature = kwargs.get("temperature", 0)
        self.max_tokens = kwargs.get("max_tokens", 4096)
        self.stream = kwargs.get("stream", True)
        self.generation_kwargs = dict(temperature=self.temperature, max_tokens=self.max_tokens, stream=self.stream)

    def generate(self, messages, use_tools: bool = False):
        self.generation_kwargs.update({"stream": True})
        response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.generation_kwargs
            )
        return messages, response
    

