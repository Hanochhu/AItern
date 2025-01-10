import pytest
import os
import yaml
from core.agent import AITernAgent

@pytest.fixture
def test_config(tmp_path):
    """创建测试配置文件"""
    # 从实际配置文件读取 API key
    with open('config.yaml', 'r') as f:
        real_config = yaml.safe_load(f)
    
    # 使用实际的 API key
    config = {
        'ai_model': {
            'provider': 'deepseek',
            'deepseek': {
                'api_key': real_config['ai_model']['deepseek']['api_key'],
                'model': 'deepseek-chat',
                'base_url': 'https://api.deepseek.com'
            }
        }
    }
    
    config_path = tmp_path / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    return str(config_path)

def test_agent_initialization(test_config):
    # 从实际配置文件读取 API key 用于比较
    with open('config.yaml', 'r') as f:
        real_config = yaml.safe_load(f)
    real_api_key = real_config['ai_model']['deepseek']['api_key']
    
    # 测试正确初始化
    agent = AITernAgent(config_path=test_config)
    assert agent.config.deepseek_api_key == real_api_key
    
    # 测试环境变量覆盖
    os.environ['DEEPSEEK_API_KEY'] = "env_test_key"
    agent = AITernAgent(config_path=test_config)
    assert agent.config.deepseek_api_key == "env_test_key"
    
    # 清理环境变量
    del os.environ['DEEPSEEK_API_KEY']

def test_implement_test(test_config):
    # 创建一个简单的测试文件
    test_content = """
def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
    assert calc.subtract(5, 3) == 2
"""
    
    test_file = "test_calculator.py"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        agent = AITernAgent(config_path=test_config)
        impl_file = agent.implement_test(test_file)
        
        # 验证生成的文件
        assert os.path.exists(impl_file)
        with open(impl_file, "r") as f:
            impl_content = f.read()
            assert "class Calculator" in impl_content
            assert "def add" in impl_content
            assert "def subtract" in impl_content
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("calculator.py"):
            os.remove("calculator.py") 