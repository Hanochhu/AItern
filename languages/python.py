import ast
import pytest
from typing import Tuple, Optional, List, Dict, Any
from .base import LanguageSupport

class PythonSupport(LanguageSupport):
    def parse_test(self, test_code: str) -> dict:
        """解析Python测试代码"""
        tree = ast.parse(test_code)
        info = {
            'classes': [],
            'functions': [],
            'assertions': [],
            'imports': set()
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info['classes'].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                info['functions'].append(node.name)
            elif isinstance(node, ast.Assert):
                info['assertions'].append(ast.unparse(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        info['imports'].add(name.name)
                else:
                    module = node.module or ''
                    for name in node.names:
                        if name.name == '*':
                            info['imports'].add(module)
                        else:
                            info['imports'].add(f"{module}.{name.name}")
                
        return info
        
    def parse_implementation(self, impl_code: str) -> dict:
        """解析Python实现代码"""
        return self.parse_test(impl_code)  # 复用解析逻辑
        
    def extract_style_guide(self, code_samples: List[str]) -> Dict[str, Any]:
        """从代码样本中提取风格指南"""
        style_guide = {
            'indentation': None,
            'quotes': None,
            'max_line_length': 0,
            'naming_conventions': {
                'class': [],
                'function': [],
                'variable': []
            }
        }
        
        for sample in code_samples:
            lines = sample.splitlines()
            
            # 分析缩进
            for line in lines:
                if line.strip() and line.startswith(' '):
                    indent = len(line) - len(line.lstrip())
                    if style_guide['indentation'] is None:
                        style_guide['indentation'] = indent
                        
            # 分析引号使用
            single_quotes = sample.count("'")
            double_quotes = sample.count('"')
            style_guide['quotes'] = "'" if single_quotes > double_quotes else '"'
            
            # 分析行长度
            max_length = max((len(line) for line in lines), default=0)
            style_guide['max_line_length'] = max(
                style_guide['max_line_length'],
                max_length
            )
            
            # 分析命名约定
            tree = ast.parse(sample)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    style_guide['naming_conventions']['class'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    style_guide['naming_conventions']['function'].append(node.name)
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        style_guide['naming_conventions']['variable'].append(node.id)
                        
        return style_guide
    
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