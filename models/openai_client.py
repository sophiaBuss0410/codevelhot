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
        self.client = openai.Client(api_key=OPENAI_API_KEY)
        self.model = kwargs.get("model_name")
        self.temperature = kwargs.get("temperature", 0)
        self.max_tokens = kwargs.get("max_tokens", 4096)
        self.stream = kwargs.get("stream", True)
        self.generation_kwargs = dict(temperature=self.temperature, max_tokens=self.max_tokens, stream=self.stream)

    def generate(self, messages):
        self.generation_kwargs.update({"stream": True})
        response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.generation_kwargs
            )
        return messages, response
    
    def off_generate(self, messages):
        generation_kwargs = dict(temperature=self.temperature, max_tokens=self.max_tokens, stream=False)
        response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **generation_kwargs
            )
        return response.choices[0].message.content
    

