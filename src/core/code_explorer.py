from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import os
import re
import json
import subprocess
from datetime import datetime

# 将来需要集成AI能力
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class CodeExplorer:
    """代码探索模块，负责代码的搜索、理解和修改"""
    
    def __init__(self, code_dir: str, config: Optional[Dict[str, Any]] = None):
        self.code_dir = Path(code_dir)
        self.exploration_history = []
        self.config = config or {}
        
        # 初始化AI相关配置
        self.ai_config = self.config.get("ai", {})
        self.model = self.ai_config.get("model", "gpt-4")
        self.api_key_env = self.ai_config.get("api_key_env", "AITERN_API_KEY")
        self.temperature = self.ai_config.get("temperature", 0.7)
        
        # 初始化探索相关配置
        self.exploration_config = self.config.get("exploration", {})
        self.search_depth = self.exploration_config.get("search_depth", 3)
        self.modification_strategy = self.exploration_config.get("modification_strategy", "incremental")
        
        # 初始化OpenAI客户端 (如果可用)
        if OPENAI_AVAILABLE:
            api_key = os.environ.get(self.api_key_env)
            if api_key:
                openai.api_key = api_key
        
    def search_code(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索相关代码
        
        Args:
            query: 搜索查询
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        logger.info(f"搜索相关代码: {query}")
        results = []
        
        # 1. 尝试根据测试名称推断相关模块
        module_name = self._infer_module_from_test(query)
        if module_name:
            module_files = self._find_module_files(module_name)
            for file_path in module_files:
                content = self._read_file(file_path)
                results.append({
                    "path": str(file_path),
                    "relevance": 0.9,  # 根据模块名推断的相关性较高
                    "reason": f"根据测试名称 '{query}' 推断出的模块 '{module_name}'",
                    "content_preview": content[:200] if content else ""
                })
        
        # 2. 使用grep搜索代码
        grep_results = self._grep_search(query)
        for result in grep_results:
            # 避免重复
            if not any(r["path"] == result["path"] for r in results):
                results.append(result)
        
        # 3. 使用语义搜索代码 (需要AI支持，这里简化处理)
        if OPENAI_AVAILABLE and len(results) < 3:
            semantic_results = self._semantic_search(query)
            for result in semantic_results:
                if not any(r["path"] == result["path"] for r in results):
                    results.append(result)
        
        logger.info(f"找到 {len(results)} 个相关代码文件")
        return results
    
    def understand_code(self, code_path: str) -> Dict[str, Any]:
        """
        理解代码结构和语义
        
        Args:
            code_path: 代码文件路径
            
        Returns:
            Dict[str, Any]: 代码理解结果
        """
        logger.info(f"分析代码: {code_path}")
        
        understanding = {
            "path": code_path,
            "language": self._detect_language(code_path),
            "timestamp": datetime.now().isoformat(),
        }
        
        # 读取文件内容
        content = self._read_file(code_path)
        if not content:
            understanding["error"] = "无法读取文件内容"
            return understanding
        
        # 分析代码结构
        understanding["structure"] = self._analyze_code_structure(code_path, content)
        
        # 如果有AI支持，进行更深入的分析
        if OPENAI_AVAILABLE:
            try:
                semantic_analysis = self._analyze_code_semantics(code_path, content)
                understanding["semantic_analysis"] = semantic_analysis
            except Exception as e:
                logger.error(f"语义分析出错: {e}")
                understanding["semantic_error"] = str(e)
        
        return understanding
    
    def generate_modification(self, 
                            test_failure: Dict[str, Any],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成代码修改方案
        
        Args:
            test_failure: 测试失败信息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 修改方案
        """
        logger.info(f"生成代码修改方案，测试: {test_failure.get('name', '')}")
        
        modification = {
            "test": test_failure,
            "timestamp": datetime.now().isoformat(),
            "strategy": self.modification_strategy,
            "changes": []
        }
        
        # 分析测试失败
        failure_type = self._analyze_failure_type(test_failure)
        modification["failure_type"] = failure_type
        
        # 根据失败类型生成修改方案
        if failure_type == "missing_module":
            module_changes = self._generate_missing_module_changes(test_failure, context)
            if module_changes:
                modification["changes"].extend(module_changes)
        
        elif failure_type == "missing_function":
            function_changes = self._generate_missing_function_changes(test_failure, context)
            if function_changes:
                modification["changes"].extend(function_changes)
        
        elif failure_type == "assertion_error":
            implementation_changes = self._generate_implementation_changes(test_failure, context)
            if implementation_changes:
                modification["changes"].extend(implementation_changes)
        
        elif failure_type == "syntax_error":
            syntax_changes = self._generate_syntax_fix_changes(test_failure, context)
            if syntax_changes:
                modification["changes"].extend(syntax_changes)
        
        else:
            # 通用修改生成逻辑
            generic_changes = self._generate_generic_changes(test_failure, context)
            if generic_changes:
                modification["changes"].extend(generic_changes)
        
        logger.info(f"生成了 {len(modification['changes'])} 个修改")
        return modification
    
    def apply_modification(self, 
                         modification: Dict[str, Any]) -> bool:
        """
        应用代码修改
        
        Args:
            modification: 修改方案
            
        Returns:
            bool: 是否成功应用修改
        """
        logger.info("应用代码修改")
        
        success = True
        applied_changes = []
        
        for change in modification.get("changes", []):
            change_type = change.get("type")
            target_path = change.get("path")
            
            try:
                if change_type == "create_file":
                    # 创建新文件
                    success = self._create_file(target_path, change.get("content", ""))
                    if success:
                        applied_changes.append(f"创建文件: {target_path}")
                    
                elif change_type == "modify_file":
                    # 修改现有文件
                    success = self._modify_file(
                        target_path, 
                        change.get("content", ""),
                        change.get("start_line"),
                        change.get("end_line")
                    )
                    if success:
                        applied_changes.append(f"修改文件: {target_path}")
                    
                elif change_type == "delete_file":
                    # 删除文件
                    success = self._delete_file(target_path)
                    if success:
                        applied_changes.append(f"删除文件: {target_path}")
                
                elif change_type == "append_to_file":
                    # 在文件末尾添加内容
                    success = self._append_to_file(target_path, change.get("content", ""))
                    if success:
                        applied_changes.append(f"追加到文件: {target_path}")
                
                elif change_type == "insert_into_file":
                    # 在指定位置插入内容
                    success = self._insert_into_file(
                        target_path,
                        change.get("content", ""),
                        change.get("line")
                    )
                    if success:
                        applied_changes.append(f"在文件中插入: {target_path}")
                
                else:
                    logger.warning(f"未知的修改类型: {change_type}")
                    success = False
                
                if not success:
                    logger.error(f"应用修改失败: {change}")
                    break
                    
            except Exception as e:
                logger.error(f"应用修改出错: {e}, change={change}")
                success = False
                break
        
        logger.info(f"应用修改{'成功' if success else '失败'}: {', '.join(applied_changes)}")
        return success
    
    def record_exploration(self, 
                          exploration: Dict[str, Any]) -> None:
        """记录探索过程"""
        self.exploration_history.append(exploration)
        
    # ===== 私有辅助方法 =====
    
    def _infer_module_from_test(self, test_name: str) -> Optional[str]:
        """根据测试名称推断模块名"""
        # 从测试名称中提取模块名
        # 假设遵循常见的命名约定，例如test_module_name -> module_name
        if test_name.startswith("test_"):
            return test_name[5:]  # 去除'test_'前缀
        return None
    
    def _find_module_files(self, module_name: str) -> List[Path]:
        """查找与模块名相关的文件"""
        files = []
        
        # 替换下划线为路径分隔符或保持原样
        module_path_variants = [
            module_name,
            module_name.replace("_", "/"),
            module_name.replace("_", ".")
        ]
        
        for variant in module_path_variants:
            # 搜索可能的Python模块文件
            pattern = f"**/{variant}.py"
            files.extend(list(self.code_dir.glob(pattern)))
            
            # 搜索同名目录下的__init__.py
            init_pattern = f"**/{variant}/__init__.py"
            files.extend(list(self.code_dir.glob(init_pattern)))
        
        return files
    
    def _grep_search(self, query: str) -> List[Dict[str, Any]]:
        """使用grep进行代码搜索"""
        results = []
        
        try:
            # 准备搜索命令，排除常见的不相关目录
            cmd = [
                "grep", "-r", "--include=*.py", 
                "-l",  # 只列出文件名
                query, str(self.code_dir)
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode not in [0, 1]:  # grep返回1表示没有匹配
                logger.warning(f"grep搜索出错: {process.stderr}")
                return results
            
            # 处理搜索结果
            files = process.stdout.strip().split("\n")
            for file_path in files:
                if file_path and os.path.exists(file_path):
                    content = self._read_file(file_path)
                    results.append({
                        "path": file_path,
                        "relevance": 0.7,  # 文本匹配的相关性适中
                        "reason": f"文本匹配查询 '{query}'",
                        "content_preview": content[:200] if content else ""
                    })
        
        except Exception as e:
            logger.error(f"grep搜索出错: {e}")
        
        return results
    
    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """使用语义搜索找到相关代码"""
        # 这里需要使用AI模型进行语义搜索，这里简化处理
        # 在真实实现中，可能需要使用嵌入模型和向量数据库
        results = []
        
        # 如果没有OpenAI支持，返回空结果
        if not OPENAI_AVAILABLE:
            return results
        
        # 在实际实现中，这里应该使用AI进行语义搜索
        # 简化起见，这里只进行基本的文件名匹配
        # TODO: 实现真正的语义搜索
        
        return results
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None
    
    def _detect_language(self, file_path: str) -> str:
        """检测文件的编程语言"""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.sh': 'bash',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _analyze_code_structure(self, file_path: str, content: str) -> Dict[str, Any]:
        """分析代码结构"""
        language = self._detect_language(file_path)
        structure = {
            "type": "file",
            "name": Path(file_path).name,
            "language": language,
            "imports": [],
            "classes": [],
            "functions": [],
            "size": len(content)
        }
        
        # 如果是Python文件，使用简单的正则表达式提取结构
        if language == 'python':
            # 提取导入语句
            import_pattern = r'^(?:from\s+(\S+)\s+import\s+(.+)|import\s+(.+))$'
            imports = []
            
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    if match.group(1) and match.group(2):  # from X import Y
                        imports.append({
                            "type": "from_import",
                            "module": match.group(1),
                            "names": [n.strip() for n in match.group(2).split(',')]
                        })
                    elif match.group(3):  # import X
                        imports.append({
                            "type": "import",
                            "module": match.group(3).strip()
                        })
            
            structure["imports"] = imports
            
            # 提取类定义
            class_pattern = r'^\s*class\s+(\w+)(?:\(([^)]*)\))?:'
            classes = []
            
            for match in re.finditer(class_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                base_classes = []
                
                if match.group(2):
                    base_classes = [c.strip() for c in match.group(2).split(',')]
                
                classes.append({
                    "name": class_name,
                    "base_classes": base_classes
                })
            
            structure["classes"] = classes
            
            # 提取函数定义
            function_pattern = r'^\s*def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:'
            functions = []
            
            for match in re.finditer(function_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2).strip() if match.group(2) else ""
                return_type = match.group(3).strip() if match.group(3) else None
                
                functions.append({
                    "name": func_name,
                    "params": params,
                    "return_type": return_type
                })
            
            structure["functions"] = functions
        
        return structure
    
    def _analyze_code_semantics(self, file_path: str, content: str) -> Dict[str, Any]:
        """使用AI分析代码语义"""
        # 需要调用OpenAI分析代码
        # 在实际实现中，这里应该调用OpenAI API
        # 简化处理，返回基本信息
        return {
            "purpose": "未知",
            "complexity": "未知",
            "quality": "未知",
            "dependencies": []
        }
    
    def _analyze_failure_type(self, test_failure: Dict[str, Any]) -> str:
        """分析测试失败类型"""
        failure_details = test_failure.get("failure", "")
        
        if "ModuleNotFoundError" in failure_details or "ImportError" in failure_details:
            return "missing_module"
        elif "AttributeError" in failure_details and "has no attribute" in failure_details:
            return "missing_function"
        elif "AssertionError" in failure_details:
            return "assertion_error"
        elif "SyntaxError" in failure_details:
            return "syntax_error"
        elif "TypeError" in failure_details:
            return "type_error"
        elif "NameError" in failure_details:
            return "name_error"
        else:
            return "unknown"
    
    def _generate_missing_module_changes(self, test_failure: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成创建缺失模块的修改"""
        changes = []
        
        # 从错误中提取模块名
        failure_details = test_failure.get("failure", "")
        module_match = re.search(r"No module named '([^']+)'", failure_details)
        
        if module_match:
            module_name = module_match.group(1)
            module_path = module_name.replace(".", "/")
            file_path = os.path.join(self.code_dir, f"{module_path}.py")
            
            # 创建简单的模块文件
            changes.append({
                "type": "create_file",
                "path": file_path,
                "content": f'"""\n{module_name} module\n"""\n\n# 自动生成的模块\n\n'
            })
        
        return changes
    
    def _generate_missing_function_changes(self, test_failure: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成创建缺失函数的修改"""
        changes = []
        
        # 从错误中提取函数名和模块名
        failure_details = test_failure.get("failure", "")
        attr_match = re.search(r"'([^']+)' has no attribute '([^']+)'", failure_details)
        
        if attr_match:
            module_name = attr_match.group(1)
            function_name = attr_match.group(2)
            
            # 查找模块文件
            module_path = module_name.replace(".", "/")
            possible_paths = [
                os.path.join(self.code_dir, f"{module_path}.py"),
                os.path.join(self.code_dir, module_path, "__init__.py")
            ]
            
            target_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    target_path = path
                    break
            
            if not target_path:
                # 如果模块文件不存在，创建它
                target_path = possible_paths[0]
                changes.append({
                    "type": "create_file",
                    "path": target_path,
                    "content": f'"""\n{module_name} module\n"""\n\n# 自动生成的模块\n\n'
                })
            
            # 从测试中提取函数签名（简化实现）
            # 在真实场景中，这里应该使用更复杂的逻辑
            function_content = f"def {function_name}():\n    \"\"\"自动生成的函数\"\"\"\n    # TODO: 实现函数\n    pass\n"
            
            changes.append({
                "type": "append_to_file",
                "path": target_path,
                "content": "\n\n" + function_content
            })
        
        return changes
    
    def _generate_implementation_changes(self, test_failure: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成函数实现的修改"""
        changes = []
        
        # 这里需要分析测试代码，识别测试的期望，然后实现功能
        # 由于涉及代码理解和生成，这个部分应该由AI完成
        # 在简化实现中，我们只能做一些基本处理
        
        # TODO: 实现更复杂的逻辑
        
        return changes
    
    def _generate_syntax_fix_changes(self, test_failure: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成语法修复的修改"""
        # 这部分依赖于具体的语法错误，需要AI介入分析和修复
        return []
    
    def _generate_generic_changes(self, test_failure: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成通用修改"""
        # 这是一个后备方案，当我们无法明确确定错误类型时使用
        # 这部分非常依赖AI的能力
        return []
    
    def _create_file(self, file_path: str, content: str) -> bool:
        """创建新文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 创建文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"创建文件失败 {file_path}: {e}")
            return False
    
    def _modify_file(self, file_path: str, content: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> bool:
        """修改文件内容"""
        try:
            # 如果未指定行号范围，替换整个文件内容
            if start_line is None or end_line is None:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            # 读取原文件
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 验证行号范围
            if start_line < 1 or end_line > len(lines) or start_line > end_line:
                logger.error(f"行号范围无效: {start_line}-{end_line}, 文件有 {len(lines)} 行")
                return False
            
            # 计算要替换的内容（注意行号从1开始，而索引从0开始）
            new_lines = lines[:start_line-1] + [content] + lines[end_line:]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
        except Exception as e:
            logger.error(f"修改文件失败 {file_path}: {e}")
            return False
    
    def _delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"删除文件失败 {file_path}: {e}")
            return False
    
    def _append_to_file(self, file_path: str, content: str) -> bool:
        """在文件末尾追加内容"""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"追加到文件失败 {file_path}: {e}")
            return False
    
    def _insert_into_file(self, file_path: str, content: str, line: int) -> bool:
        """在指定行插入内容"""
        try:
            # 读取原文件
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 验证行号
            if line < 1 or line > len(lines) + 1:
                logger.error(f"行号无效: {line}, 文件有 {len(lines)} 行")
                return False
            
            # 插入内容
            new_lines = lines[:line-1] + [content] + lines[line-1:]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
        except Exception as e:
            logger.error(f"在文件中插入失败 {file_path}: {e}")
            return False
