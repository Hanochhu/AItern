import os
import logging
from typing import Optional
from models.openai_model import OpenAIModel
from models.deepseek_model import DeepSeekModel
from languages.python import PythonSupport
from utils.config import Config

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AITernAgent:
    def __init__(self, config_path: Optional[str] = None):
        """初始化AI代理"""
        self.config = Config(config_path)
        
        # 根据配置选择AI模型
        if self.config.ai_provider == 'openai':
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required")
            self.ai_model = OpenAIModel(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model
            )
        elif self.config.ai_provider == 'deepseek':
            if not self.config.deepseek_api_key:
                raise ValueError("DeepSeek API key is required")
            self.ai_model = DeepSeekModel(
                api_key=self.config.deepseek_api_key,
                model=self.config.deepseek_model,
                base_url=self.config.deepseek_base_url
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.ai_provider}")
            
        self.language_support = PythonSupport()
        
    def implement_test(self, test_file: str) -> str:
        """根据测试文件生成实现代码"""
        # 读取测试文件
        with open(test_file, 'r') as f:
            test_code = f.read()
            
        # 解析测试代码
        test_info = self.language_support.parse_test(test_code)
        logger.debug(f"Parsed test info: {test_info}")
        
        # 生成实现代码
        implementation = self.ai_model.generate_implementation(
            test_code=test_code,
            language='python'
        )
        logger.debug(f"Generated implementation:\n{implementation}")
        
        # 验证实现代码
        if not self.language_support.validate_implementation(implementation):
            logger.error(f"Invalid implementation:\n{implementation}")
            raise ValueError("Generated implementation is not valid Python code")
            
        # 保存实现代码
        impl_file = test_file.replace('test_', '')
        with open(impl_file, 'w') as f:
            f.write(implementation)
            
        # 运行测试
        success, error = self.language_support.run_test(test_file, impl_file)
        if not success:
            raise RuntimeError(f"Implementation failed tests: {error}")
            
        return impl_file 