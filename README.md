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

这会在你的项目目录下创建一个 `env` 文件，你可以根据你的环境进行配置。项目中提供了一个 `.env` 文件作为模板。请记得将 `env` 文件加入到你的 `.gitignore` 中，以避免将密钥等敏感信息上传到代码仓库。

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

## 配置说明

AItern通过项目根目录下的 `env` 文件进行配置。执行 `aitern . init` 时，会从 `.env` 模板文件复制生成 `env` 文件。

一个典型的 `.env` 模板文件内容如下：

```dotenv
# AItern Configuration Template

# 测试目录
AITERN_TEST_DIR="tests"

# 探索记录目录
AITERN_RECORD_DIR="aitern_explorations"

# 最大迭代次数
AITERN_MAX_ITERATIONS=10

# 使用的AI模型 (例如, gpt-4, gpt-3.5-turbo)
AITERN_AI_MODEL="gpt-4"

# 你的AI模型API密钥
AITERN_API_KEY="YOUR_API_KEY_HERE"

# AI模型生成的多样性 (0.0 到 1.0)
AITERN_AI_TEMPERATURE=0.7

# 代码探索深度
AITERN_EXPLORATION_SEARCH_DEPTH=3

# 代码修改策略 (例如, incremental)
AITERN_EXPLORATION_MODIFICATION_STRATEGY="incremental"
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
│   └── utils/         # 工具函数
├── tests/             # 测试用例
├── docs/              # 文档
├── requirements.txt   # 项目依赖
└── README.md          # 项目说明
```

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
