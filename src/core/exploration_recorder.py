from typing import List, Dict, Any
import json
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExplorationRecorder:
    """探索记录模块，负责记录和管理探索过程"""
    
    def __init__(self, record_dir: str):
        self.record_dir = Path(record_dir)
        self.record_dir.mkdir(parents=True, exist_ok=True)
        self.current_exploration = None
        
    def start_exploration(self, 
                         test_case: Dict[str, Any],
                         initial_code: Dict[str, Any]) -> str:
        """开始新的探索记录"""
        exploration_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_exploration = {
            "id": exploration_id,
            "start_time": datetime.now().isoformat(),
            "test_case": test_case,
            "initial_code": initial_code,
            "steps": []
        }
        return exploration_id
        
    def record_step(self, 
                   step_type: str,
                   details: Dict[str, Any]) -> None:
        """记录探索步骤"""
        if not self.current_exploration:
            logger.warning("没有活动的探索记录")
            return
            
        step = {
            "timestamp": datetime.now().isoformat(),
            "type": step_type,
            "details": details
        }
        self.current_exploration["steps"].append(step)
        
    def end_exploration(self, 
                       success: bool,
                       final_code: Dict[str, Any]) -> None:
        """结束探索记录"""
        if not self.current_exploration:
            logger.warning("没有活动的探索记录")
            return
            
        self.current_exploration.update({
            "end_time": datetime.now().isoformat(),
            "success": success,
            "final_code": final_code
        })
        
        # 保存探索记录
        record_path = self.record_dir / f"{self.current_exploration['id']}.json"
        with open(record_path, 'w') as f:
            json.dump(self.current_exploration, f, indent=2)
            
        self.current_exploration = None
        
    def get_exploration_history(self) -> List[Dict[str, Any]]:
        """获取探索历史"""
        history = []
        for record_file in self.record_dir.glob("*.json"):
            with open(record_file) as f:
                history.append(json.load(f))
        return sorted(history, key=lambda x: x["start_time"], reverse=True)
