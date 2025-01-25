import ast
import subprocess
import tempfile
import os
from typing import Tuple, List, Dict, Any, Optional
import pytest
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
            'indentation': '4 spaces',  # Python默认缩进
            'quotes': 'single',  # 默认使用单引号
            'max_line_length': '79',  # PEP 8标准
            'class_naming': 'PascalCase',
            'function_naming': 'snake_case',
            'variable_naming': 'snake_case'
        }
        
        for sample in code_samples:
            try:
                tree = ast.parse(sample)
                
                # 分析字符串引号使用
                for node in ast.walk(tree):
                    if isinstance(node, ast.Str):
                        if node.s.startswith("'"):
                            style_guide['quotes'] = 'single'
                        elif node.s.startswith('"'):
                            style_guide['quotes'] = 'double'
                            
                # 分析行长度
                lines = sample.splitlines()
                max_length = max(len(line) for line in lines) if lines else 79
                style_guide['max_line_length'] = str(max_length)
                
            except SyntaxError:
                continue
                
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
            # 创建临时目录用于测试
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 复制测试文件和实现文件到临时目录
                test_name = os.path.basename(test_file)
                impl_name = os.path.basename(impl_file)
                tmp_test = os.path.join(tmp_dir, test_name)
                tmp_impl = os.path.join(tmp_dir, impl_name)
                
                with open(test_file, 'r') as f:
                    test_content = f.read()
                with open(impl_file, 'r') as f:
                    impl_content = f.read()
                    
                with open(tmp_test, 'w') as f:
                    f.write(test_content)
                with open(tmp_impl, 'w') as f:
                    f.write(impl_content)
                    
                # 运行pytest
                result = pytest.main(['-v', tmp_test])
                
                return result == 0, ""  # pytest.ExitCode.OK == 0
                
        except Exception as e:
            return False, str(e) 