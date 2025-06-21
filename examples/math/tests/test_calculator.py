"""
测试计算器模块的基本功能
"""
import pytest
from math_app.calculator import Calculator

def test_add():
    """测试加法功能"""
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0

def test_subtract():
    """测试减法功能"""
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(1, 1) == 0
    assert calc.subtract(0, 5) == -5

def test_multiply():
    """测试乘法功能"""
    calc = Calculator()
    assert calc.multiply(2, 3) == 6
    assert calc.multiply(-1, 2) == -2
    assert calc.multiply(0, 5) == 0

def test_divide():
    """测试除法功能"""
    calc = Calculator()
    assert calc.divide(6, 3) == 2
    assert calc.divide(5, 2) == 2.5
    assert calc.divide(-6, 2) == -3
    
    # 测试除以零的情况
    with pytest.raises(ValueError):
        calc.divide(5, 0) 