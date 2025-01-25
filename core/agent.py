import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from models.openai_model import OpenAIModel
from models.deepseek_model import DeepSeekModel
from models.base import AIModel
from languages.python import PythonSupport
from languages.base import LanguageSupport
from utils.config import Config
from utils.imports import ImportAnalyzer
from utils.git_manager import GitManager
from utils.git_config import GitConfig

logger = logging.getLogger(__name__)

class AITernAgent:
    """AI驱动的测试实现代理
    
    负责协调AI模型、语言支持、Git操作等组件，
    实现从测试到代码的自动化流程。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化AI代理
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
            
        Raises:
            ValueError: 当配置无效或缺少必要的API密钥时
        """
        self.config = Config(config_path)
        self.project_root = str(Path.cwd())
        self.import_analyzer = ImportAnalyzer(self.project_root)
        
        # 创建 Git 配置
        git_config = GitConfig(
            reviewers=self.config.get('git.reviewers', []),
            labels=self.config.get('git.labels', ['ai-generated']),
            base_branch=self.config.get('git.base_branch', 'main'),
            push_to_remote=self.config.get('git.push_to_remote', True)
        )
        self.git_manager = GitManager(self.project_root, git_config)
        
        # 初始化AI模型
        self.ai_model = self._initialize_ai_model()
        
        # 初始化语言支持
        self.language_support = PythonSupport()  # 目前只支持Python
        
    def _initialize_ai_model(self) -> AIModel:
        """初始化AI模型
        
        Returns:
            AIModel: 初始化好的AI模型实例
            
        Raises:
            ValueError: 当AI提供商配置无效时
        """
        if self.config.ai_provider == 'openai':
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required")
            return OpenAIModel(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model
            )
        elif self.config.ai_provider == 'deepseek':
            if not self.config.deepseek_api_key:
                raise ValueError("DeepSeek API key is required")
            return DeepSeekModel(
                api_key=self.config.deepseek_api_key,
                model=self.config.deepseek_model,
                base_url=self.config.deepseek_base_url
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.ai_provider}")
            
    def _get_project_context(self, test_file: str) -> Dict[str, Any]:
        """获取项目上下文信息
        
        Args:
            test_file: 测试文件路径
            
        Returns:
            Dict[str, Any]: 包含项目上下文的字典
        """
        context = {
            'test_file': test_file,
            'test_content': '',
            'related_files': [],
            'related_contents': {},
            'project_structure': {},
            'imports': set(),
            'style_guide': {},
            'dependencies': {}
        }
        
        # 读取测试文件
        with open(test_file, 'r', encoding='utf-8') as f:
            test_content = f.read()
            context['test_content'] = test_content
            
        # 分析测试文件中的导入
        test_info = self.language_support.parse_test(test_content)
        context['imports'].update(test_info.get('imports', []))
            
        # 查找相关实现文件
        test_dir = os.path.dirname(test_file)
        impl_dir = test_dir.replace('tests', '')
        test_name = os.path.basename(test_file)
        impl_name = test_name.replace('test_', '')
        impl_path = os.path.join(impl_dir, impl_name)
        
        # 如果实现文件已存在，分析它
        if os.path.exists(impl_path):
            context['related_files'].append(impl_path)
            with open(impl_path, 'r', encoding='utf-8') as f:
                impl_content = f.read()
                context['related_contents'][impl_path] = impl_content
                impl_info = self.language_support.parse_implementation(impl_content)
                context['imports'].update(impl_info.get('imports', []))
                
        # 分析项目结构
        for root, dirs, files in os.walk(self.project_root):
            if any(d.startswith('.') for d in root.split(os.sep)):
                continue
            rel_path = os.path.relpath(root, self.project_root)
            context['project_structure'][rel_path] = {
                'dirs': [d for d in dirs if not d.startswith('.')],
                'files': [f for f in files if f.endswith('.py')]
            }
            
        # 分析依赖
        if context['imports']:
            context['dependencies'] = self.import_analyzer.analyze_imports(
                context['imports']
            )
            for module_name, content in context['dependencies'].items():
                file_path = self.import_analyzer.find_module_file(module_name.split('.')[0])
                if file_path:
                    context['related_files'].append(file_path)
                    context['related_contents'][file_path] = content
            
        # 分析代码风格
        if context['related_contents']:
            context['style_guide'] = self.language_support.extract_style_guide(
                list(context['related_contents'].values())
            )
            
        return context
        
    def _validate_generated_code(self, implementation: str, test_file: str, impl_file: str) -> bool:
        """验证生成的代码
        
        Args:
            implementation: 生成的实现代码
            test_file: 测试文件路径
            impl_file: 实现文件路径
            
        Returns:
            bool: 验证是否通过
        """
        # 基本语法检查
        if not self.language_support.validate_implementation(implementation):
            logger.error("Generated code failed syntax validation")
            return False
        
        # 保存实现代码到临时文件
        tmp_impl_file = impl_file + '.tmp'
        try:
            with open(tmp_impl_file, 'w') as f:
                f.write(implementation)
            
            # 运行测试
            success, error = self.language_support.run_test(test_file, tmp_impl_file)
            if not success:
                logger.error(f"Implementation failed tests: {error}")
                return False
            
            return True
        
        finally:
            # 清理临时文件
            if os.path.exists(tmp_impl_file):
                os.remove(tmp_impl_file)
        
    def implement_test(
        self, 
        test_file: str, 
        create_pr: bool = True,
        max_retries: int = 3
    ) -> str:
        """根据测试文件生成实现代码
        
        Args:
            test_file: 测试文件路径
            create_pr: 是否创建 PR
            max_retries: 最大重试次数
            
        Returns:
            str: 实现文件路径
        """
        try:
            # 创建新的实现分支
            branch_name = self.git_manager.create_implementation_branch(test_file)
            logger.info(f"Working on branch: {branch_name}")
            
            # 获取项目上下文
            context = self._get_project_context(test_file)
            logger.debug(f"Project context: {context}")
            
            # 确定实现文件路径
            impl_file = test_file.replace('test_', '')
            
            # 尝试生成实现
            for attempt in range(max_retries):
                try:
                    # 生成实现代码
                    implementation = self.ai_model.generate_implementation(
                        test_code=context['test_content'],
                        language='python',
                        context=context
                    )
                    logger.debug(f"Generated implementation (attempt {attempt + 1}):\n{implementation}")
                    
                    # 验证实现
                    if self._validate_generated_code(implementation, test_file, impl_file):
                        # 保存实现代码
                        with open(impl_file, 'w') as f:
                            f.write(implementation)
                            
                        # 提交实现代码
                        self.git_manager.commit_implementation(impl_file, test_file)
                        
                        # 创建 PR（如果需要）
                        if create_pr:
                            pr_url = self.git_manager.create_pull_request(impl_file, test_file)
                            logger.info(f"Created PR: {pr_url}")
                        
                        return impl_file
                        
                    # 如果验证失败，更新上下文包含错误信息
                    context['previous_attempt'] = {
                        'implementation': implementation,
                        'attempt_number': attempt + 1
                    }
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                        
            raise RuntimeError(f"Failed to generate valid implementation after {max_retries} attempts")
            
        except Exception as e:
            logger.error(f"Implementation failed: {str(e)}")
            raise 