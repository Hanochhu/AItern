"""
计算器模块
"""

class Calculator:
    """简单的计算器类，提供基本的数学运算功能"""
    
    def __init__(self):
        """初始化计算器对象"""
        pass
    
    def add(self, a, b):
        """
        计算两个数的和
        
        Args:
            a: 第一个数
            b: 第二个数
            
        Returns:
            两个数的和
        """
        return a + b
    
    def subtract(self, a, b):
        """
        计算两个数的差
        
        Args:
            a: 第一个数
            b: 第二个数
            
        Returns:
            a减去b的结果
        """
        return a - b
    
    # 故意省略乘法和除法的实现，让AItern自动完成 