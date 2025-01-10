from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AIModel(ABC):
    """AI模型的基础接口"""
    
    @abstractmethod
    def generate_implementation(
        self, 
        test_code: str, 
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """根据测试代码生成实现代码
        
        Args:
            test_code: 测试代码内容
            language: 编程语言
            context: 项目上下文信息，包含相关文件内容
            
        Returns:
            str: 生成的实现代码
        """
        pass 