import pytest
import os
from pathlib import Path
from utils.imports import ImportAnalyzer

@pytest.fixture
def test_project(tmp_path):
    """创建测试项目结构"""
    # 创建一个简单的包结构
    package_dir = tmp_path / "mypackage"
    package_dir.mkdir()
    (package_dir / "__init__.py").touch()
    
    # 创建一个模块文件
    calculator_content = """
class Calculator:
    def add(self, a, b):
        return a + b
"""
    (package_dir / "calculator.py").write_text(calculator_content.strip())
    
    return tmp_path

def test_import_analyzer(test_project):
    # 初始化导入分析器
    analyzer = ImportAnalyzer(str(test_project))
    
    # 测试模块查找
    module_path = analyzer.find_module_file("mypackage.calculator")
    assert module_path is not None
    assert Path(module_path).name == "calculator.py"
    
    # 测试导入分析
    imports = {"mypackage.calculator"}
    analyzed = analyzer.analyze_imports(imports)
    assert "mypackage.calculator" in analyzed
    assert "class Calculator" in analyzed["mypackage.calculator"] 