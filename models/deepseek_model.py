import openai  # DeepSeek 使用 OpenAI 兼容接口
from typing import Optional

try:
    from .base import AIModel  # 当作为包导入时使用
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.base import AIModel  # 当直接运行文件时使用

class DeepSeekModel(AIModel):
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com"):
        self.client = openai.Client(
            api_key=api_key,
            base_url=base_url
        )
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
            ]
        )
        
        return response.choices[0].message.content
