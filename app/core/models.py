import os
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

class LLMBase:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class DeepSeekModel(LLMBase):
    def __init__(self, model_name: str = "deepseek-chat"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_base="https://api.deepseek.com/v1",
            openai_api_key=os.environ["DEEPSEEK_API_KEY"],
            temperature=0,
        )

    def generate(self, prompt: str) -> str:
        response = self.llm.predict(prompt)
        return response
