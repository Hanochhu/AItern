import pytest
import os
import yaml
import logging
import git
import shutil
from unittest.mock import patch, MagicMock
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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

@pytest.fixture
def git_repo(tmp_path):
    """创建测试用 Git 仓库"""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)
    
    # 创建初始提交
    readme = repo_path / "README.md"
    readme.write_text("# Test Repository")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    
    return repo_path

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

def test_implement_test(test_config, caplog):
    caplog.set_level(logging.DEBUG)
    
    # 创建一个带有导入的测试文件
    test_content = """
from calculator import Calculator
import math

def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
    assert calc.multiply(2, math.pi) > 6
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
            print(f"\nGenerated implementation:\n{impl_content}")
            assert "class Calculator" in impl_content
            assert "def add" in impl_content
            assert "def multiply" in impl_content
            assert "import math" in impl_content  # 验证导入被保留
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("calculator.py"):
            os.remove("calculator.py")

def test_implement_test_with_git(test_config, git_repo, caplog):
    caplog.set_level(logging.DEBUG)
    
    # 切换到测试仓库目录
    original_dir = os.getcwd()
    os.chdir(git_repo)
    
    try:
        # 创建测试文件
        test_content = """
from calculator import Calculator
import math

def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
    assert calc.multiply(2, math.pi) > 6
"""
        test_file = "test_calculator.py"
        with open(test_file, "w") as f:
            f.write(test_content)
            
        # 初始化 agent 并实现测试
        agent = AITernAgent(config_path=test_config)
        impl_file = agent.implement_test(test_file)
        
        # 验证 Git 操作
        repo = git.Repo()
        assert "impl/calculator-" in repo.active_branch.name
        
        # 验证实现文件
        assert os.path.exists(impl_file)
        with open(impl_file, "r") as f:
            impl_content = f.read()
            assert "class Calculator" in impl_content
            assert "def add" in impl_content
            assert "def multiply" in impl_content
            
        # 验证提交
        latest_commit = repo.head.commit
        assert "AI: Implement" in latest_commit.message
        assert impl_file in latest_commit.stats.files
        
    finally:
        # 清理并恢复目录
        os.chdir(original_dir)
        shutil.rmtree(git_repo) 

def test_implement_test_with_pr(test_config, git_repo, caplog):
    caplog.set_level(logging.DEBUG)
    
    # 设置 GitHub token (使用 mock token 进行测试)
    os.environ['GITHUB_TOKEN'] = 'test_token'
    
    # 模拟 GitHub API
    with patch('github.Github') as mock_github:
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.html_url = 'https://github.com/owner/repo/pull/1'
        mock_repo.create_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # 切换到测试仓库目录
        original_dir = os.getcwd()
        os.chdir(git_repo)
        
        try:
            # 创建测试文件
            test_content = """
from calculator import Calculator
import math

def test_calculator():
    calc = Calculator()
    assert calc.add(1, 2) == 3
"""
            test_file = "test_calculator.py"
            with open(test_file, "w") as f:
                f.write(test_content)
                
            # 初始化 agent 并实现测试
            agent = AITernAgent(config_path=test_config)
            impl_file = agent.implement_test(test_file, create_pr=True)
            
            # 验证 PR 创建
            mock_repo.create_pull.assert_called_once()
            assert "impl/calculator-" in mock_repo.create_pull.call_args[1]['head']
            
        finally:
            # 清理并恢复目录
            os.chdir(original_dir)
            shutil.rmtree(git_repo)
            del os.environ['GITHUB_TOKEN'] 