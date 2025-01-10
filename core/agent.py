import os
import logging
from typing import Optional, List
from models.openai_model import OpenAIModel
from models.deepseek_model import DeepSeekModel
from languages.python import PythonSupport
from utils.config import Config
from utils.imports import ImportAnalyzer

logger = logging.getLogger(__name__)

class AITernAgent:
    def __init__(self, config_path: Optional[str] = None):
        """初始化AI代理"""
        self.config = Config(config_path)
        self.project_root = os.getcwd()
        self.import_analyzer = ImportAnalyzer(self.project_root)
        
        # 初始化AI模型
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
        
    def _get_project_context(self, test_file: str) -> dict:
        """获取项目上下文信息"""
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
        with open(test_file, 'r') as f:
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
            with open(impl_path, 'r') as f:
                impl_content = f.read()
                context['related_contents'][impl_path] = impl_content
                # 分析实现文件中的导入
                impl_info = self.language_support.parse_implementation(impl_content)
                context['imports'].update(impl_info.get('imports', []))
                
        # 分析项目结构
        for root, dirs, files in os.walk(self.project_root):
            if any(d.startswith('.') for d in root.split(os.sep)):
                continue  # 跳过隐藏目录
            rel_path = os.path.relpath(root, self.project_root)
            context['project_structure'][rel_path] = {
                'dirs': [d for d in dirs if not d.startswith('.')],
                'files': [f for f in files if f.endswith('.py')]
            }
            
        # 查找并分析相关依赖文件
        if context['imports']:
            context['dependencies'] = self.import_analyzer.analyze_imports(
                context['imports']
            )
            # 将依赖文件也添加到相关文件列表中
            for module_name, content in context['dependencies'].items():
                file_path = self.import_analyzer.find_module_file(module_name.split('.')[0])
                if file_path:
                    context['related_files'].append(file_path)
                    context['related_contents'][file_path] = content
            
        # 分析代码风格
        if context['related_contents']:
            # 从现有代码中提取风格指南
            context['style_guide'] = self.language_support.extract_style_guide(
                list(context['related_contents'].values())
            )
            
        return context
        
    def implement_test(self, test_file: str) -> str:
        """根据测试文件生成实现代码"""
        # 获取项目上下文
        context = self._get_project_context(test_file)
        logger.debug(f"Project context: {context}")
        
        # 生成实现代码
        implementation = self.ai_model.generate_implementation(
            test_code=context['test_content'],
            language='python',
            context=context  # 传递上下文信息
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