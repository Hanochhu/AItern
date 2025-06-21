from typing import Optional
import git
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BranchManager:
    """分支管理模块，负责创建和管理代码分支"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        
    def create_branch(self, branch_name: str) -> bool:
        """创建新的探索分支"""
        try:
            self.repo.git.checkout('HEAD', b=branch_name)
            return True
        except git.GitCommandError as e:
            logger.error(f"创建分支失败: {e}")
            return False
            
    def switch_branch(self, branch_name: str) -> bool:
        """切换到指定分支"""
        try:
            self.repo.git.checkout(branch_name)
            return True
        except git.GitCommandError as e:
            logger.error(f"切换分支失败: {e}")
            return False
            
    def commit_changes(self, message: str) -> Optional[str]:
        """提交代码修改"""
        try:
            self.repo.git.add(A=True)
            commit = self.repo.index.commit(message)
            return commit.hexsha
        except git.GitCommandError as e:
            logger.error(f"提交修改失败: {e}")
            return None
            
    def merge_branch(self, 
                    source_branch: str,
                    target_branch: str = 'main') -> bool:
        """合并分支"""
        try:
            self.repo.git.checkout(target_branch)
            self.repo.git.merge(source_branch)
            return True
        except git.GitCommandError as e:
            logger.error(f"合并分支失败: {e}")
            return False
