import pytest
import os
from languages.python import PythonSupport

@pytest.fixture
def python_support():
    return PythonSupport()

@pytest.fixture
def sample_test_code():
    return """
import math
from calculator import Calculator

def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
    assert calc.multiply(2, math.pi) > 6
"""

@pytest.fixture
def sample_impl_code():
    return """
import math

class Calculator:
    def add(self, a, b):
        return a + b
        
    def multiply(self, a, b):
        return a * b
"""

def test_parse_test(python_support, sample_test_code):
    """测试测试代码解析"""
    info = python_support.parse_test(sample_test_code)
    
    assert 'imports' in info
    assert 'math' in info['imports']
    assert 'calculator.Calculator' in info['imports']
    
    assert 'functions' in info
    assert 'test_calculator' in info['functions']
    
    assert 'assertions' in info
    assert any('calc.add(1, 2) == 3' in assertion for assertion in info['assertions'])
    assert any('calc.multiply(2, math.pi) > 6' in assertion for assertion in info['assertions'])

def test_parse_implementation(python_support, sample_impl_code):
    """测试实现代码解析"""
    info = python_support.parse_implementation(sample_impl_code)
    
    assert 'imports' in info
    assert 'math' in info['imports']
    
    assert 'classes' in info
    assert 'Calculator' in info['classes']
    
    assert 'functions' in info
    assert 'add' in info['functions']
    assert 'multiply' in info['functions']

def test_validate_implementation(python_support, sample_impl_code):
    """测试代码验证"""
    assert python_support.validate_implementation(sample_impl_code)
    
    # 测试无效代码
    invalid_code = """
    class Invalid:
        def broken(self):
            return a +  # 语法错误
    """
    assert not python_support.validate_implementation(invalid_code)

def test_extract_style_guide(python_support):
    """测试代码风格提取"""
    code_samples = [
        """
        def test_function():
            x = 'single quotes'
            return x
        """,
        """
        class TestClass:
            def method(self):
                y = "double quotes"
                return y
        """
    ]
    
    style_guide = python_support.extract_style_guide(code_samples)
    
    assert 'indentation' in style_guide
    assert 'quotes' in style_guide
    assert 'max_line_length' in style_guide
    assert 'class_naming' in style_guide
    assert 'function_naming' in style_guide
    assert 'variable_naming' in style_guide

def test_run_test(python_support, tmp_path):
    """测试运行测试"""
    # 创建测试文件
    test_content = """
def test_simple():
    assert 1 + 1 == 2
"""
    test_file = tmp_path / "test_simple.py"
    test_file.write_text(test_content)
    
    # 创建实现文件
    impl_content = """
# 空实现文件
"""
    impl_file = tmp_path / "simple.py"
    impl_file.write_text(impl_content)
    
    # 运行测试
    success, error = python_support.run_test(str(test_file), str(impl_file))
    assert success
    assert error == ""
    
    # 测试失败的情况
    test_content = """
def test_failing():
    assert False
"""
    test_file.write_text(test_content)
    success, error = python_support.run_test(str(test_file), str(impl_file))
    assert not success 