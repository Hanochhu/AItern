from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional

class LanguageSupport(ABC):
    """编程语言支持的基类"""
    
    @abstractmethod
    def parse_test(self, test_code: str) -> dict:
        """解析测试代码
        
        Args:
            test_code: 测试代码字符串
            
        Returns:
            dict: 包含测试信息的字典
        """
        pass
        
    @abstractmethod
    def parse_implementation(self, impl_code: str) -> dict:
        """解析实现代码
        
        Args:
            impl_code: 实现代码字符串
            
        Returns:
            dict: 包含实现信息的字典
        """
        pass
        
    @abstractmethod
    def extract_style_guide(self, code_samples: List[str]) -> Dict[str, Any]:
        """从代码样本中提取代码风格指南
        
        Args:
            code_samples: 代码样本列表
            
        Returns:
            Dict[str, Any]: 代码风格指南
        """
        pass
        
    @abstractmethod
    def validate_implementation(self, implementation: str) -> bool:
        """验证实现代码
        
        Args:
            implementation: 实现代码字符串
            
        Returns:
            bool: 代码是否有效
        """
        pass
        
    @abstractmethod
    def run_test(self, test_file: str, impl_file: str) -> Tuple[bool, Optional[str]]:
        """运行测试
        
        Args:
            test_file: 测试文件路径
            impl_file: 实现文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (测试是否通过, 错误信息)
        """
        pass 