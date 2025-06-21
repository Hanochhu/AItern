import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理模块，负责加载和管理配置"""
    
    DEFAULT_CONFIG = {
        "test_dir": "tests",                      # 测试目录
        "record_dir": ".aitern/explorations",     # 探索记录目录
        "max_iterations": 10,                     # 最大迭代次数
        "ai": {
            "model": "gpt-4",                     # 使用的AI模型
            "api_key_env": "AITERN_API_KEY",      # API密钥环境变量名
            "temperature": 0.7                    # 生成多样性
        },
        "exploration": {
            "search_depth": 3,                    # 代码搜索深度
            "modification_strategy": "incremental" # 代码修改策略
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，为None则使用默认配置
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> bool:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 是否成功加载
        """
        path = Path(config_path)
        
        if not path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return False
        
        try:
            with open(path) as f:
                user_config = json.load(f)
                self._update_config(user_config)
            logger.info(f"成功加载配置: {config_path}")
            return True
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return False
    
    def _update_config(self, user_config: Dict[str, Any]) -> None:
        """递归更新配置"""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict) and isinstance(self.config[key], dict):
                self._update_config_dict(self.config[key], value)
            else:
                self.config[key] = value
    
    def _update_config_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """递归更新字典"""
        for key, value in source.items():
            if key in target and isinstance(value, dict) and isinstance(target[key], dict):
                self._update_config_dict(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """获取嵌套配置值"""
        current = self.config
        for key in keys:
            if key not in current:
                return default
            current = current[key]
        return current
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
    
    def save_config(self, config_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 是否成功保存
        """
        path = Path(config_path)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"成功保存配置到: {config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

