import os
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.test_manager import TestManager
from src.core.code_explorer import CodeExplorer
from src.core.branch_manager import BranchManager
from src.core.exploration_recorder import ExplorationRecorder

logger = logging.getLogger(__name__)

class AIternManager:
    """AItern系统主协调器，负责协调各个模块的工作"""
    
    def __init__(self, target_project_path: str, config: Dict[str, Any] = None):
        """
        初始化AItern管理器
        
        Args:
            target_project_path: 目标项目的路径
            config: 配置信息
        """
        self.target_project_path = os.path.abspath(target_project_path)
        self.config = config or {}
        
        # 初始化各个模块
        self.test_manager = TestManager(
            test_dir=os.path.join(self.target_project_path, self.config.get('test_dir', 'tests'))
        )
        self.code_explorer = CodeExplorer(
            code_dir=self.target_project_path
        )
        self.branch_manager = BranchManager(
            repo_path=self.target_project_path
        )
        self.exploration_recorder = ExplorationRecorder(
            record_dir=os.path.join(self.target_project_path, self.config.get('record_dir', '.aitern/explorations'))
        )
        
        # 探索状态
        self.current_exploration_id = None
        self.current_branch = None
        self.exploration_results = {}
        
    def start_exploration(self, test_names: Optional[List[str]] = None) -> str:
        """
        开始新的代码探索过程
        
        Args:
            test_names: 指定要运行的测试名称，为None则运行所有测试
            
        Returns:
            exploration_id: 探索会话的ID
        """
        logger.info(f"开始新的代码探索，目标项目: {self.target_project_path}")
        
        # 解析测试用例
        test_cases = self.test_manager.parse_tests()
        if not test_cases:
            raise ValueError("未找到测试用例")
        
        # 创建新的探索分支
        branch_name = f"aitern-exploration-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        if not self.branch_manager.create_branch(branch_name):
            raise RuntimeError(f"无法创建分支: {branch_name}")
        
        self.current_branch = branch_name
        logger.info(f"创建新分支: {branch_name}")
        
        # 开始记录探索
        initial_code_files = self._get_initial_code_state()
        self.current_exploration_id = self.exploration_recorder.start_exploration(
            test_case=test_cases,
            initial_code=initial_code_files
        )
        
        logger.info(f"开始探索会话: {self.current_exploration_id}")
        
        return self.current_exploration_id
    
    def explore(self, max_iterations: int = 10) -> Dict[str, Any]:
        """
        执行代码探索过程
        
        Args:
            max_iterations: 最大迭代次数
            
        Returns:
            exploration_results: 探索结果
        """
        if not self.current_exploration_id or not self.current_branch:
            raise ValueError("请先调用 start_exploration() 开始探索")
        
        logger.info(f"开始执行探索迭代，最大迭代次数: {max_iterations}")
        
        iteration = 0
        success = False
        
        while iteration < max_iterations and not success:
            iteration += 1
            logger.info(f"开始第 {iteration} 次迭代")
            
            # 1. 运行测试
            test_results = self.test_manager.run_tests()
            
            # 记录测试结果
            self.exploration_recorder.record_step(
                step_type="test_execution",
                details={"iteration": iteration, "results": test_results}
            )
            
            # 2. 如果所有测试通过，探索成功
            if test_results.get("success", False):
                logger.info("所有测试通过，探索成功")
                success = True
                break
            
            # 3. 获取失败的测试
            failed_tests = self.test_manager.get_failed_tests()
            
            # 4. 分析测试结果
            analysis = self.test_manager.analyze_test_results(test_results)
            
            # 记录分析结果
            self.exploration_recorder.record_step(
                step_type="test_analysis",
                details={"iteration": iteration, "analysis": analysis}
            )
            
            # 5. 搜索相关代码
            code_search_results = []
            for test in failed_tests:
                search_results = self.code_explorer.search_code(test.get("name", ""))
                code_search_results.extend(search_results)
            
            # 记录代码搜索结果
            self.exploration_recorder.record_step(
                step_type="code_search",
                details={"iteration": iteration, "results": code_search_results}
            )
            
            # 6. 理解代码
            code_understanding = {}
            for result in code_search_results:
                code_path = result.get("path")
                if code_path:
                    code_understanding[code_path] = self.code_explorer.understand_code(code_path)
            
            # 记录代码理解结果
            self.exploration_recorder.record_step(
                step_type="code_understanding",
                details={"iteration": iteration, "understanding": code_understanding}
            )
            
            # 7. 生成代码修改
            modifications = []
            for test in failed_tests:
                mod = self.code_explorer.generate_modification(
                    test_failure=test,
                    context={"code_understanding": code_understanding}
                )
                if mod:
                    modifications.append(mod)
            
            # 记录代码修改计划
            self.exploration_recorder.record_step(
                step_type="modification_plan",
                details={"iteration": iteration, "modifications": modifications}
            )
            
            # 8. 应用代码修改
            applied_mods = []
            for mod in modifications:
                success = self.code_explorer.apply_modification(mod)
                applied_mods.append({"modification": mod, "success": success})
            
            # 记录代码修改应用结果
            self.exploration_recorder.record_step(
                step_type="modification_applied",
                details={"iteration": iteration, "applied_modifications": applied_mods}
            )
            
            # 9. 提交代码修改
            commit_message = f"AItern探索迭代 {iteration}: 尝试修复失败的测试"
            commit_sha = self.branch_manager.commit_changes(commit_message)
            
            # 记录代码提交
            self.exploration_recorder.record_step(
                step_type="code_commit",
                details={"iteration": iteration, "commit_sha": commit_sha, "message": commit_message}
            )
            
            logger.info(f"完成第 {iteration} 次迭代")
        
        # 探索结束
        final_code_state = self._get_current_code_state()
        
        self.exploration_recorder.end_exploration(
            success=success,
            final_code=final_code_state
        )
        
        exploration_result = {
            "exploration_id": self.current_exploration_id,
            "branch_name": self.current_branch,
            "iterations": iteration,
            "success": success,
            "final_state": final_code_state
        }
        
        self.exploration_results[self.current_exploration_id] = exploration_result
        
        logger.info(f"探索完成: success={success}, iterations={iteration}")
        
        return exploration_result
    
    def apply_successful_exploration(self, exploration_id: Optional[str] = None) -> bool:
        """
        应用成功的探索结果（合并分支）
        
        Args:
            exploration_id: 要应用的探索ID，为None则使用当前探索
            
        Returns:
            bool: 是否成功合并
        """
        target_id = exploration_id or self.current_exploration_id
        if not target_id:
            raise ValueError("未指定探索ID")
        
        result = self.exploration_results.get(target_id)
        if not result:
            # 尝试从记录中加载结果
            history = self.exploration_recorder.get_exploration_history()
            for item in history:
                if item["id"] == target_id:
                    result = {
                        "exploration_id": item["id"],
                        "branch_name": None,  # 需要从记录中获取
                        "success": item.get("success", False)
                    }
                    break
        
        if not result:
            raise ValueError(f"未找到探索结果: {target_id}")
        
        if not result.get("success", False):
            logger.warning(f"探索 {target_id} 未成功，不进行合并")
            return False
        
        branch_name = result.get("branch_name")
        if not branch_name:
            raise ValueError(f"未找到探索分支名: {target_id}")
        
        logger.info(f"合并探索分支 {branch_name} 到主分支")
        return self.branch_manager.merge_branch(branch_name)
    
    def _get_initial_code_state(self) -> Dict[str, Any]:
        """获取初始代码状态"""
        # TODO: 实现代码状态获取逻辑
        return {"timestamp": datetime.now().isoformat()}
    
    def _get_current_code_state(self) -> Dict[str, Any]:
        """获取当前代码状态"""
        # TODO: 实现代码状态获取逻辑
        return {"timestamp": datetime.now().isoformat()}

