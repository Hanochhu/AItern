import pytest
from languages.python import PythonSupport

def test_parse_test():
    python_support = PythonSupport()
    test_code = """
def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
    assert calc.subtract(5, 3) == 2
    """
    
    info = python_support.parse_test(test_code)
    assert 'functions' in info
    assert 'test_calculator' in info['functions']
    assert len(info['assertions']) == 2

def test_validate_implementation():
    python_support = PythonSupport()
    
    valid_code = """
class Calculator:
    def add(self, a, b):
        return a + b
    """
    assert python_support.validate_implementation(valid_code) == True
    
    invalid_code = """
class Calculator
    def add(self, a, b):
        return a + b
    """
    assert python_support.validate_implementation(invalid_code) == False 