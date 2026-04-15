# 🤖 智谱AI GitHub自动化系统

## ✅ 已完成配置

本系统已经完全配置好，包含以下功能：

- ✅ 自动分析带 `claude-auto` 标签的GitHub Issues
- ✅ 使用智谱AI GLM-4-Flash模型进行分析
- ✅ 自动在Issue中发表分析结果
- ✅ 完整的错误处理和日志记录
- ✅ 所有依赖已配置完成

## 📋 系统要求

- ✅ GitHub仓库已配置
- ✅ GitHub Secrets已设置 (ZHIPU_API_KEY)
- ✅ 工作流文件已推送
- ✅ Python脚本已优化

## 🚀 如何测试

### 方法1：自动触发（推荐）

1. **创建Issue**
   ```
   访问：https://github.com/yyd841122/ragchatbot-codebase/issues
   点击 "New issue"
   ```

2. **填写Issue内容**
   ```markdown
   ## 🧪 测试智谱AI自动化

   请分析当前项目并给出改进建议。
   ```

3. **添加标签**
   - 在右侧找到 "Labels"
   - 点击 "Labels"
   - 输入或选择 `claude-auto`
   - 点击 "Submit new issue"

4. **等待处理**
   - 系统会在1-3分钟内自动处理
   - 刷新Issue页面查看AI回复

### 方法2：手动触发

1. **访问Actions页面**
   ```
   https://github.com/yyd841122/ragchatbot-codebase/actions
   ```

2. **选择工作流**
   - 左侧选择 "Zhipu AI Issue Handler"
   - 点击 "Run workflow"

3. **输入参数**
   - Branch: main
   - Issue number: 输入要处理的Issue编号
   - 点击 "Run workflow"

## 📊 监控执行

### 通过网页

```
1. 访问 Actions 页面
2. 点击具体运行记录
3. 查看每个步骤的日志
```

### 通过命令行

```bash
# 查看最近的运行
gh run list --repo yyd841122/ragchatbot-codebase

# 查看具体运行的日志
gh run view <run-id> --repo yyd841122/ragchatbot-codebase --log

# 实时监控
gh run watch --repo yyd841122/ragchatbot-codebase
```

## 🔍 成功的标志

当系统正常工作时，你会看到：

### GitHub Actions
```
✅ Checkout repository
✅ Install Node.js
✅ Install Python
✅ Install system dependencies
✅ Install Python dependencies
✅ Verify installation
✅ Process Issue with Zhipu AI
```

### Issue评论
```markdown
## 🤖 Zhipu AI 分析

[详细的AI分析和建议]

正在实现修复方案，请稍候...
```

## 📝 使用建议

### 日常使用

1. **创建Issue时直接加标签**
   - 创建Issue时选择 `claude-auto` 标签
   - 系统会自动触发处理

2. **给现有Issue添加标签**
   - 打开任意Issue
   - 点击 "Settings" → "Labels"
   - 添加 `claude-auto` 标签

3. **查看AI建议**
   - 在Issue评论中查看AI分析
   - 根据建议进行修改
   - 可以继续讨论和追问

### 最佳实践

1. **清晰的Issue描述**
   - 详细描述问题
   - 提供重现步骤
   - 包含错误日志

2. **合适的标签**
   - `claude-auto`: 触发AI处理
   - `bug`: Bug报告
   - `enhancement`: 功能增强
   - `documentation`: 文档改进

3. **人工审核**
   - 始终审核AI的建议
   - 测试所有修改
   - 验证解决方案的有效性

## 🛠️ 技术细节

### 工作流程

```
Issue创建 + claude-auto标签
    ↓
GitHub Actions自动触发
    ↓
安装依赖 (Node.js + Python + zhipuai)
    ↓
验证环境
    ↓
获取Issue内容
    ↓
调用智谱AI API
    ↓
生成分析结果
    ↓
在Issue中发表评论
    ↓
完成
```

### 技术栈

- **GitHub Actions**: 工作流自动化
- **Python 3.13**: 脚本语言
- **智谱AI**: GLM-4-Flash模型
- **PyGithub**: GitHub API客户端
- **Node.js 20**: 系统依赖

### 环境变量

- `ZHIPU_API_KEY`: 智谱AI密钥（在GitHub Secrets中）
- `GITHUB_TOKEN`: GitHub自动提供
- `REPO_NAME`: 仓库名称
- `ISSUE_NUMBER`: Issue编号

## 💰 成本说明

- **智谱AI**: 按实际使用量计费
- **GLM-4-Flash**: 约 ¥0.001-0.01/次
- **GitHub Actions**: 完全免费
- **预估成本**: 每个Issue < ¥0.1

## 🔒 安全说明

- ✅ API Key存储在GitHub Secrets中
- ✅ 仅在运行时注入到环境变量
- ✅ 不会出现在日志中
- ✅ 所有AI建议需人工审核

## 📞 获取帮助

如果遇到问题：

1. **查看Actions日志**
   - GitHub仓库 → Actions → 具体运行

2. **查看Issue评论**
   - AI会在那里提供详细分析

3. **检查环境变量**
   ```bash
   gh secret list --repo yyd841122/ragchatbot-codebase
   ```

4. **本地测试**
   ```bash
   uv run python test_zhipu_api.py
   ```

## 🎉 开始使用

现在你可以直接创建一个带 `claude-auto` 标签的Issue来测试系统！

**快速测试：**
1. 创建新Issue
2. 标题：`测试自动化系统`
3. 内容：任意描述
4. 添加标签：`claude-auto`
5. 提交并等待AI回复

祝你使用愉快！🚀
