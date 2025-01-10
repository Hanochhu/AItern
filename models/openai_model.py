import openai
from typing import Optional
from .base import AIModel

class OpenAIModel(AIModel):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.Client(api_key=api_key)
        self.model = model
        
    def generate_implementation(self, test_code: str, language: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个专业的{language}开发者。请根据测试代码生成符合要求的实现代码。"
                },
                {
                    "role": "user",
                    "content": f"请根据以下测试代码生成实现代码:\n\n{test_code}"
                }
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content 