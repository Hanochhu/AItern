import ast
import pytest
from typing import Tuple, Optional
from .base import LanguageSupport

class PythonSupport(LanguageSupport):
    def parse_test(self, test_code: str) -> dict:
        """解析Python测试代码，提取关键信息"""
        tree = ast.parse(test_code)
        info = {
            'classes': [],
            'functions': [],
            'assertions': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info['classes'].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                info['functions'].append(node.name)
            elif isinstance(node, ast.Assert):
                info['assertions'].append(ast.unparse(node))
                
        return info
    
    def validate_implementation(self, implementation: str) -> bool:
        """验证Python实现代码的语法"""
        try:
            ast.parse(implementation)
            return True
        except SyntaxError:
            return False
    
    def run_test(self, test_file: str, impl_file: str) -> Tuple[bool, Optional[str]]:
        """运行Python测试"""
        try:
            pytest.main([test_file, "-v"])
            return True, None
        except Exception as e:
            return False, str(e) 