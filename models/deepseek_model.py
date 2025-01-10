import openai
import re
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
        
    def _extract_code(self, content: str) -> str:
        """从 Markdown 格式的回答中提取代码部分"""
        # 尝试匹配 ```python ... ``` 格式
        pattern = r"```python\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()
            
        # 如果没有找到 Python 代码块，尝试匹配任意代码块
        pattern = r"```\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()
            
        # 如果没有代码块，返回原始内容
        return content.strip()
        
    def generate_implementation(self, test_code: str, language: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"你是一个专业的{language}开发者。"
                        "请根据测试代码生成实现代码。"
                        "只返回代码，不需要任何解释。"
                    )
                },
                {
                    "role": "user",
                    "content": f"请根据以下测试代码生成实现代码:\n\n{test_code}"
                }
            ]
        )
        
        content = response.choices[0].message.content
        return self._extract_code(content)
