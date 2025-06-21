#!/usr/bin/env python
import argparse
import os
import sys
import logging
from typing import Dict, Any

from src.core.aitern_manager import AIternManager
from src.config.config_manager import ConfigManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('aitern')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='AItern - 基于测试驱动开发的AI代码探索工具'
    )
    
    # 必要参数
    parser.add_argument(
        'project_path',
        help='目标项目路径'
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 探索命令
    explore_parser = subparsers.add_parser('explore', help='开始代码探索')
    explore_parser.add_argument(
        '--tests', '-t',
        nargs='+',
        help='要运行的测试名称，不指定则运行所有测试'
    )
    explore_parser.add_argument(
        '--max-iterations', '-m',
        type=int,
        default=10,
        help='最大探索迭代次数'
    )
    explore_parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    # 应用探索结果命令
    apply_parser = subparsers.add_parser('apply', help='应用探索结果')
    apply_parser.add_argument(
        'exploration_id',
        help='要应用的探索ID'
    )
    
    # 列出探索历史命令
    list_parser = subparsers.add_parser('list', help='列出探索历史')
    
    # 初始化配置命令
    init_parser = subparsers.add_parser('init', help='初始化配置')
    init_parser.add_argument(
        '--output', '-o',
        default='.aitern/config.json',
        help='配置文件输出路径'
    )
    
    return parser.parse_args()

def load_config(config_path: str = None) -> Dict[str, Any]:
    """加载配置文件"""
    config_manager = ConfigManager(config_path)
    return config_manager.config

def main():
    """主函数"""
    args = parse_args()
    
    if not os.path.exists(args.project_path):
        logger.error(f"项目路径不存在: {args.project_path}")
        sys.exit(1)
    
    if args.command == 'init':
        # 初始化配置文件
        output_path = os.path.join(args.project_path, args.output)
        config_manager = ConfigManager()
        if config_manager.save_config(output_path):
            logger.info(f"配置文件已创建: {output_path}")
        else:
            logger.error(f"无法创建配置文件: {output_path}")
            sys.exit(1)
        return
    
    # 加载配置
    config_path = None
    if hasattr(args, 'config') and args.config:
        config_path = args.config
    else:
        # 尝试查找默认配置
        default_config = os.path.join(args.project_path, '.aitern/config.json')
        if os.path.exists(default_config):
            config_path = default_config
    
    config = load_config(config_path)
    
    # 如果命令行指定了最大迭代次数，覆盖配置
    if hasattr(args, 'max_iterations') and args.max_iterations:
        config['max_iterations'] = args.max_iterations
    
    try:
        # 初始化AItern管理器
        manager = AIternManager(args.project_path, config)
        
        if args.command == 'explore':
            # 开始探索
            exploration_id = manager.start_exploration(args.tests)
            logger.info(f"开始探索: {exploration_id}")
            
            # 执行探索
            result = manager.explore(config.get('max_iterations', 10))
            
            if result['success']:
                logger.info(f"探索成功! 分支: {result['branch_name']}")
                logger.info(f"可以使用 'aitern {args.project_path} apply {result['exploration_id']}' 应用探索结果")
            else:
                logger.warning(f"探索未能解决所有测试失败，迭代次数: {result['iterations']}")
                logger.info(f"尝试的探索分支: {result['branch_name']}")
        
        elif args.command == 'apply':
            # 应用探索结果
            success = manager.apply_successful_exploration(args.exploration_id)
            if success:
                logger.info(f"成功应用探索结果: {args.exploration_id}")
            else:
                logger.error(f"无法应用探索结果: {args.exploration_id}")
        
        elif args.command == 'list':
            # 列出探索历史
            history = manager.exploration_recorder.get_exploration_history()
            
            if not history:
                logger.info("没有探索历史记录")
            else:
                logger.info(f"找到 {len(history)} 条探索记录:")
                for item in history:
                    status = "成功" if item.get("success", False) else "失败"
                    logger.info(f"ID: {item['id']}, 状态: {status}, 开始时间: {item['start_time']}")
        
        else:
            logger.error(f"未知命令: {args.command}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"运行过程中出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

