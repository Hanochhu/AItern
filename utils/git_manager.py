import git
import logging
from typing import Optional
import os
from utils.git_config import GitConfig

logger = logging.getLogger(__name__)

class GitManager:
    def __init__(self, repo_path: str = '.', config: Optional[GitConfig] = None):
        """初始化 Git 管理器
        
        Args:
            repo_path: Git 仓库路径
            config: Git 配置
        """
        try:
            self.repo = git.Repo(repo_path)
            self.config = config or GitConfig()
        except git.InvalidGitRepositoryError:
            raise ValueError(f"{repo_path} 不是一个有效的 Git 仓库")
            
    def create_implementation_branch(self, test_file: str) -> str:
        """创建实现分支
        
        Args:
            test_file: 测试文件名，用于生成分支名
            
        Returns:
            str: 新分支名
        """
        # 确保在主分支
        current = self.repo.active_branch
        if current.name != self.config.base_branch:
            self.repo.heads[self.config.base_branch].checkout()
            
        # 创建新分支
        base_name = test_file.replace('test_', '').replace('.py', '')
        branch_name = f"{self.config.branch_prefix}{base_name}-{git.utils.strftime('%Y%m%d')}"
        
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        
        logger.info(f"Created and checked out new branch: {branch_name}")
        return branch_name
        
    def commit_implementation(self, impl_file: str, test_file: str) -> None:
        """提交实现代码
        
        Args:
            impl_file: 实现文件路径
            test_file: 测试文件路径
        """
        # 添加文件到暂存区
        self.repo.index.add([impl_file])
        
        # 创建提交信息
        commit_message = f"AI: Implement {impl_file} for {test_file}"
        self.repo.index.commit(commit_message)
        
        logger.info(f"Committed implementation: {commit_message}")

    def create_pull_request(self, impl_file: str, test_file: str) -> str:
        """创建 Pull Request
        
        Args:
            impl_file: 实现文件路径
            test_file: 测试文件路径
            
        Returns:
            str: PR URL
        """
        if not self.config.push_to_remote:
            logger.info("Skipping PR creation as push_to_remote is disabled")
            return None
            
        try:
            import github
            from github import Github
            
            current_branch = self.repo.active_branch.name
            
            # 获取远程仓库信息
            remote_url = self.repo.remotes.origin.url
            repo_name = remote_url.split('/')[-2:]
            repo_name = '/'.join(repo_name).replace('.git', '')
            
            # 推送分支
            self.repo.remotes.origin.push(current_branch)
            
            # 创建 PR
            g = Github(os.getenv('GITHUB_TOKEN'))
            repo = g.get_repo(repo_name)
            
            # 使用模板生成 PR 内容
            title = self.config.pr_title_template.format(test_file=test_file)
            body = self.config.pr_body_template.format(
                impl_file=impl_file,
                test_file=test_file
            )
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=current_branch,
                base=self.config.base_branch
            )
            
            # 添加审查者
            if self.config.reviewers:
                pr.add_to_assignees(*self.config.reviewers)
                
            # 添加标签
            if self.config.labels:
                pr.add_to_labels(*self.config.labels)
            
            logger.info(f"Created PR: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            logger.error(f"Failed to create PR: {str(e)}")
            raise 