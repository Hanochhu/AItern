import os
import ast
from typing import Set, Dict, Optional
from pathlib import Path

class ImportAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.module_cache: Dict[str, str] = {}
        
    def find_module_file(self, module_name: str) -> Optional[str]:
        """查找模块文件的路径"""
        if module_name in self.module_cache:
            return self.module_cache[module_name]
            
        # 转换模块名为路径
        module_parts = module_name.split('.')
        module_path = os.path.join(*module_parts)
        
        possible_paths = [
            self.project_root / f"{module_path}.py",
            self.project_root / module_path / "__init__.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.module_cache[module_name] = str(path)
                return str(path)
                
        return None
        
    def analyze_imports(self, imports: Set[str]) -> Dict[str, str]:
        """分析导入的模块"""
        result = {}
        for import_name in imports:
            file_path = self.find_module_file(import_name)
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        result[import_name] = content.strip()
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    result[import_name] = ""
        return result 