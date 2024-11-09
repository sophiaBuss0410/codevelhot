from utils.helpers import singleton, generator_simulator
from utils.functions_utils import functions_infos, handle_tool_call

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
        if use_tools:
            self.generation_kwargs.update({"stream": False})
            response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=functions_infos,
                    **self.generation_kwargs
                )
            print(response)
            print(response.choices)
            if response.choices[0].finish_reason == "tool_calls":
                print("Executing a tool call")
                tool_response = handle_tool_call(response)
                print("Tool call response is: ", tool_response)
                if tool_response:
                    messages.append(response.choices[0].message)
                    messages.extend(tool_response)
                self.generation_kwargs.update({"stream": True})
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **self.generation_kwargs
                )
                return messages, response
            return messages, generator_simulator(response.choices[0].message.content)
            
        else:
            self.generation_kwargs.update({"stream": True})
            response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **self.generation_kwargs
                )
            return messages, response
    

