# AItern

AItern 是一个基于测试驱动开发(TDD)的AI驱动代码探索工具。它能够自动运行测试用例，并通过AI agent探索代码实现方案，直到测试通过。

## 功能特点

- 支持测试驱动开发流程
- 自动创建和管理代码分支
- AI驱动的代码探索和修改
- 记录探索路径和结果
- 支持多种编程语言
- 可配置的探索策略

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/AItern.git
cd AItern

# 安装依赖
pip install -r requirements.txt

# 安装为命令行工具
pip install -e .
```

## 使用方法

### 1. 初始化配置

在你的项目目录中初始化AItern配置：

```bash
cd 你的项目目录
aitern . init
```

这会在你的项目目录下创建 `.aitern/config.json` 文件，你可以根据需要修改配置。

### 2. 编写测试用例

在你的项目中编写测试用例，例如使用pytest：

```python
# tests/test_example.py
def test_function_to_implement():
    from your_module import function_to_implement
    result = function_to_implement(5, 10)
    assert result == 15
```

### 3. 开始代码探索

运行AItern开始探索代码实现：

```bash
aitern . explore
```

AItern会：
1. 创建一个新的git分支用于探索
2. 运行测试用例并分析失败原因
3. 使用AI生成代码实现
4. 迭代修改直到测试通过

### 4. 查看探索历史

查看AItern的探索记录：

```bash
aitern . list
```

### 5. 应用探索结果

如果探索成功，你可以应用结果（合并分支）：

```bash
aitern . apply 探索ID
```

### 高级用法

#### 指定测试运行

只运行特定的测试：

```bash
aitern . explore --tests test_function_one test_function_two
```

#### 配置最大迭代次数

```bash
aitern . explore --max-iterations 20
```

#### 使用自定义配置文件

```bash
aitern . explore --config custom_config.json
```

## 配置文件说明

AItern的配置文件（`.aitern/config.json`）包含以下内容：

```json
{
  "test_dir": "tests",                     // 测试目录
  "record_dir": ".aitern/explorations",    // 探索记录目录
  "max_iterations": 10,                    // 最大迭代次数
  "ai": {
    "model": "gpt-4",                      // 使用的AI模型
    "api_key_env": "AITERN_API_KEY",       // API密钥环境变量名
    "temperature": 0.7                     // 生成多样性
  },
  "exploration": {
    "search_depth": 3,                     // 代码搜索深度
    "modification_strategy": "incremental" // 代码修改策略
  }
}
```

## 工作流程

1. 用户编写测试 → 描述期望的功能行为
2. AItern创建新分支 → 所有修改在新分支，不影响原代码
3. AI分析测试 → 理解需要实现什么功能
4. AI生成/修改代码 → 尝试实现功能
5. 运行测试 → 检查实现是否正确
6. 如果失败，重复步骤3-5 → 直到测试通过或达到最大迭代次数
7. 合并成功的探索 → 将AI实现的功能合并到主分支

## 项目结构

```
AItern/
├── src/                # 源代码
│   ├── core/          # 核心功能模块
│   ├── agents/        # AI agent实现
│   ├── utils/         # 工具函数
│   └── config/        # 配置文件
├── tests/             # 测试用例
├── docs/              # 文档
├── requirements.txt   # 项目依赖
└── README.md          # 项目说明
```

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
