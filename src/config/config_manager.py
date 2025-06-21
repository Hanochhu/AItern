import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理模块，负责从环境变量和env文件加载配置"""

    def __init__(self, project_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            project_path: 项目根目录路径
        """
        self.config: Dict[str, Any] = {}
        self._load_config(project_path)

    def _load_config(self, project_path: Optional[str] = None):
        """
        从env文件或环境变量加载配置。
        env文件中的配置会覆盖系统环境变量。
        """
        # 默认值
        self.config = {
            "test_dir": "tests",
            "record_dir": "aitern_explorations",
            "max_iterations": 10,
            "ai_model": "gpt-4",
            "ai_temperature": 0.7,
            "exploration_search_depth": 3,
            "exploration_modification_strategy": "incremental",
            "api_key": None
        }

        env_path = None
        if project_path:
            env_path = os.path.join(project_path, 'env')
            if os.path.exists(env_path):
                load_dotenv(dotenv_path=env_path, override=True)
            else:
                logger.warning(f"env配置文件不存在: {env_path}，将只使用环境变量和默认值。")
        else:
            # 如果没有项目路径，则尝试在当前目录或上层目录寻找env文件
            env_path = find_dotenv('env', usecwd=True)
            if env_path:
                load_dotenv(dotenv_path=env_path, override=True)

        self.config["test_dir"] = os.getenv("AITERN_TEST_DIR", self.config["test_dir"])
        self.config["record_dir"] = os.getenv("AITERN_RECORD_DIR", self.config["record_dir"])
        self.config["max_iterations"] = int(os.getenv("AITERN_MAX_ITERATIONS", self.config["max_iterations"]))
        self.config["ai_model"] = os.getenv("AITERN_AI_MODEL", self.config["ai_model"])
        self.config["api_key"] = os.getenv("AITERN_API_KEY", self.config["api_key"])
        self.config["ai_temperature"] = float(os.getenv("AITERN_AI_TEMPERATURE", self.config["ai_temperature"]))
        self.config["exploration_search_depth"] = int(os.getenv("AITERN_EXPLORATION_SEARCH_DEPTH", self.config["exploration_search_depth"]))
        self.config["exploration_modification_strategy"] = os.getenv("AITERN_EXPLORATION_MODIFICATION_STRATEGY", self.config["exploration_modification_strategy"])
        
        logger.info(f"配置已加载。测试目录: {self.config['test_dir']}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """为了兼容性，模拟获取嵌套配置值"""
        if len(keys) == 2 and keys[0] == 'ai':
            if keys[1] == 'model':
                return self.config.get('ai_model', default)
            if keys[1] == 'temperature':
                return self.config.get('ai_temperature', default)
            if keys[1] == 'api_key_env':
                # api_key_env的概念被移除了，直接返回api_key
                return self.config.get('api_key', default)
        
        if len(keys) == 2 and keys[0] == 'exploration':
            if keys[1] == 'search_depth':
                return self.config.get('exploration_search_depth', default)
            if keys[1] == 'modification_strategy':
                return self.config.get('exploration_modification_strategy', default)

        key = '_'.join(keys)
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value

