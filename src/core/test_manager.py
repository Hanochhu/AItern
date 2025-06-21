from typing import List, Dict, Any
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

class TestManager:
    """测试管理模块，负责解析、执行和分析测试用例"""
    
    def __init__(self, test_dir: str):
        self.test_dir = Path(test_dir)
        self.test_results = {}
        
    def parse_tests(self) -> List[Dict[str, Any]]:
        """解析测试目录中的测试用例"""
        logger.info(f"解析测试用例: {self.test_dir}")
        test_cases = []
        
        # 搜索所有测试文件
        test_files = list(self.test_dir.glob("**/test_*.py"))
        
        for test_file in test_files:
            # 分析测试文件中的测试用例
            relative_path = test_file.relative_to(self.test_dir)
            test_cases.append({
                "file": str(relative_path),
                "path": str(test_file),
                "name": test_file.stem,
                "module": ".".join(relative_path.with_suffix("").parts).replace("/", ".")
            })
        
        logger.info(f"找到 {len(test_cases)} 个测试文件")
        return test_cases
        
    def run_tests(self) -> Dict[str, Any]:
        """运行测试用例并收集结果"""
        logger.info(f"运行测试: {self.test_dir}")
        
        results = {
            "success": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        try:
            # 使用pytest运行测试
            cmd = ["python", "-m", "pytest", str(self.test_dir), "-v"]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # 解析测试输出
            output = process.stdout
            error = process.stderr
            exit_code = process.returncode
            
            # 保存原始测试结果
            self.test_results = {
                "exit_code": exit_code,
                "output": output,
                "error": error
            }
            
            # 简单解析测试结果
            results["success"] = exit_code == 0
            
            # 提取测试统计信息（简化处理，实际应该使用pytest的JSON报告）
            for line in output.split("\n"):
                if line.startswith("=") and "passed" in line:
                    stats = line.strip("=").strip()
                    parts = stats.split(", ")
                    
                    for part in parts:
                        if "passed" in part:
                            results["passed"] = int(part.split()[0])
                        elif "failed" in part:
                            results["failed"] = int(part.split()[0])
                        elif "skipped" in part:
                            results["skipped"] = int(part.split()[0])
            
            results["total"] = results["passed"] + results["failed"] + results["skipped"]
            
            # 记录详细的测试结果
            # TODO: 实现更精确的测试结果解析
            
        except Exception as e:
            logger.error(f"运行测试失败: {e}")
            results["error"] = str(e)
        
        return results
        
    def analyze_test_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试结果，生成修复建议"""
        logger.info(f"分析测试结果")
        
        analysis = {
            "success": results.get("success", False),
            "failed_count": results.get("failed", 0),
            "suggestions": []
        }
        
        if analysis["success"]:
            logger.info("所有测试通过，无需修复")
            return analysis
        
        # 分析测试输出，提取失败信息
        output = self.test_results.get("output", "")
        
        # 从测试输出中提取错误信息和建议
        error_sections = []
        current_section = []
        in_error_section = False
        
        for line in output.split("\n"):
            if line.startswith("E       "):
                in_error_section = True
                current_section.append(line[8:])  # 去除前缀 "E       "
            elif in_error_section and line.strip() and not line.startswith("_"):
                current_section.append(line)
            elif in_error_section and not line.strip():
                if current_section:
                    error_sections.append("\n".join(current_section))
                    current_section = []
                    in_error_section = False
                    
        # 如果最后一个错误部分没有被处理
        if current_section:
            error_sections.append("\n".join(current_section))
            
        # 生成简单的修复建议
        for error in error_sections:
            suggestion = {
                "error": error,
                "suggestion": "根据错误信息修复代码实现"
            }
            
            if "AssertionError" in error:
                suggestion["type"] = "assertion_error"
                suggestion["suggestion"] = "修改代码实现以满足断言条件"
            elif "ImportError" in error or "ModuleNotFoundError" in error:
                suggestion["type"] = "import_error"
                suggestion["suggestion"] = "创建缺失的模块或函数"
            elif "AttributeError" in error:
                suggestion["type"] = "attribute_error"
                suggestion["suggestion"] = "实现缺失的属性或方法"
            elif "TypeError" in error:
                suggestion["type"] = "type_error"
                suggestion["suggestion"] = "确保函数参数和返回值类型正确"
            
            analysis["suggestions"].append(suggestion)
        
        return analysis
        
    def get_failed_tests(self) -> List[Dict[str, Any]]:
        """获取失败的测试用例"""
        logger.info("获取失败的测试用例")
        
        failed_tests = []
        output = self.test_results.get("output", "")
        
        # 解析测试输出，找出失败的测试
        current_test = None
        collecting_failure = False
        failure_details = []
        
        for line in output.split("\n"):
            if "FAILED" in line and "::" in line:
                # 提取测试文件和测试名称
                parts = line.split("FAILED")[0].strip()
                test_path = parts.split(" ")[0]
                
                if "::" in test_path:
                    file_path, test_name = test_path.split("::", 1)
                    
                    current_test = {
                        "file": file_path,
                        "name": test_name,
                        "failure": "",
                        "details": []
                    }
                    collecting_failure = True
                    failure_details = []
            
            elif collecting_failure:
                if line.strip() and (line.startswith("E ") or line.startswith("_")):
                    if line.startswith("E "):
                        failure_details.append(line[2:])
                elif not line.strip() and failure_details:
                    # 空行表示错误详情结束
                    if current_test:
                        current_test["failure"] = "\n".join(failure_details)
                        current_test["details"] = failure_details.copy()
                        failed_tests.append(current_test)
                        current_test = None
                        collecting_failure = False
                        failure_details = []
        
        # 处理最后一个失败的测试
        if current_test and failure_details:
            current_test["failure"] = "\n".join(failure_details)
            current_test["details"] = failure_details.copy()
            failed_tests.append(current_test)
        
        logger.info(f"找到 {len(failed_tests)} 个失败的测试")
        return failed_tests
