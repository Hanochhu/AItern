import openai
import re
from typing import Optional, Dict, Any

try:
    from .base import AIModel
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.base import AIModel

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
        
    def generate_implementation(
        self, 
        test_code: str, 
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        # 构建系统提示
        system_content = [
            f"你是一个专业的{language}开发者。",
            "请根据测试代码和项目上下文生成实现代码。",
            "生成的代码应该与项目现有代码风格保持一致。",
            "必须包含所有必要的导入语句。",
            "只返回代码，不需要任何解释。"
        ]
        
        # 构建用户提示
        user_content = [
            "请生成完整的实现代码，包括所有必要的导入语句。",
            f"\n测试代码:\n{test_code}"
        ]
        
        # 添加上下文信息
        if context and context['imports']:
            user_content.append("\n需要的导入:")
            for imp in context['imports']:
                user_content.append(f"- {imp}")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "\n".join(system_content)
                },
                {
                    "role": "user",
                    "content": "\n".join(user_content)
                }
            ]
        )
        
        content = response.choices[0].message.content
        return self._extract_code(content)
