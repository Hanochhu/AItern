from abc import ABC, abstractmethod
from typing import Tuple, Optional

class LanguageSupport(ABC):
    """编程语言支持的基础接口"""
    
    @abstractmethod
    def parse_test(self, test_code: str) -> dict:
        """解析测试代码，提取关键信息
        
        Args:
            test_code: 测试代码内容
            
        Returns:
            dict: 包含解析后的信息，如类名、方法名等
        """
        pass
    
    @abstractmethod
    def validate_implementation(self, implementation: str) -> bool:
        """验证生成的实现代码是否符合语言规范
        
        Args:
            implementation: 实现代码
            
        Returns:
            bool: 验证是否通过
        """
        pass
    
    @abstractmethod
    def run_test(self, test_file: str, impl_file: str) -> Tuple[bool, Optional[str]]:
        """运行测试
        
        Args:
            test_file: 测试文件路径
            impl_file: 实现文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (测试是否通过，错误信息)
        """
        pass 