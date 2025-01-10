import os
import yaml
from typing import Optional, Dict, Any

class Config:
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        self.config_path = config_path or os.path.join(os.getcwd(), 'config.yaml')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}. "
                "Please copy config.yaml.template to config.yaml and fill in your settings."
            )
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @property
    def ai_provider(self) -> str:
        """获取AI提供商"""
        return self.config.get('ai_model', {}).get('provider', 'openai')
    
    @property
    def openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return (
            os.getenv('OPENAI_API_KEY') or 
            self.config.get('ai_model', {}).get('openai', {}).get('api_key')
        )
    
    @property
    def openai_model(self) -> str:
        """获取OpenAI模型名称"""
        return self.config.get('ai_model', {}).get('openai', {}).get('model', 'gpt-4')
    
    @property
    def deepseek_api_key(self) -> str:
        """获取DeepSeek API密钥"""
        return (
            os.getenv('DEEPSEEK_API_KEY') or 
            self.config.get('ai_model', {}).get('deepseek', {}).get('api_key')
        )
    
    @property
    def deepseek_model(self) -> str:
        """获取DeepSeek模型名称"""
        return self.config.get('ai_model', {}).get('deepseek', {}).get('model', 'deepseek-coder-33b-instruct')
    
    @property
    def deepseek_base_url(self) -> str:
        """获取DeepSeek base URL"""
        return (
            os.getenv('DEEPSEEK_BASE_URL') or 
            self.config.get('ai_model', {}).get('deepseek', {}).get('base_url', 'https://api.deepseek.com')
        ) 