"""
语言支持模块
提供对不同编程语言的支持，包括代码解析、验证和测试运行等功能
"""

from .base import LanguageSupport
from .python import PythonSupport

__all__ = ['LanguageSupport', 'PythonSupport'] 