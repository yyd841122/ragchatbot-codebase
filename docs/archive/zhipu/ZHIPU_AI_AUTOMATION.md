> **⚠️ 归档文档**
> 本文档已归档，内容可能过时。
> 请优先使用 [Zhipu AI Agent 文档导航](../../ZHIPU_GUIDE.md) 作为当前入口。
>
> **归档日期**：2026-04-23
> **归档原因**：早期自动化系统说明，使用 Anthropic API，已被使用 Zhipu AI 的新系统取代
>
> ---

# 🚀 智谱 AI 自动化 Issue 处理系统 - 快速开始

## ✨ 已完成修改

已将所有 Claude AI 相关代码修改为使用**智谱 AI**，无需额外付费！

### 🔄 主要变更
- ✅ API 从 Anthropic 改为智谱 AI
- ✅ 使用与项目相同的 GLM-4-Flash 模型
- ✅ 中文提示词，更符合国内使用习惯
- ✅ 无需 Anthropic 账号或 Pro 订阅

## 📋 安装步骤

### 1. 获取智谱 API Key

1. 访问 https://open.bigmodel.cn/usercenter/apikeys
2. 登录或注册账号
3. 创建新的 API Key
4. 复制 key

### 2. 设置 GitHub Secrets

使用 GitHub CLI 设置：

```bash
# 设置智谱 API Key
gh secret set ZHIPU_API_KEY --repo yyd841122/ragchatbot-codebase
# 粘贴你的 API Key

# 验证设置
gh secret list --repo yyd841122/ragchatbot-codebase
```

### 3. 推送到 GitHub

```bash
# 添加所有修改
git add .github/

# 提交
git commit -m "Update: Use Zhipu AI instead of Anthropic API"

# 推送
git push origin main
```

## 🎯 使用方法

### 方式 1: 自动触发（推荐）

给任何 Issue 添加 `claude-auto` 标签，系统会自动处理：

1. 在 GitHub Issue 中点击 "Settings"
2. 添加标签 "claude-auto"
3. 等待智谱 AI 分析和处理
4. 在 Issue 中查看 AI 的回复和建议

### 方式 2: 手动触发

1. 访问 GitHub Actions 页面
2. 选择 "Zhipu AI Issue Handler" 工作流
3. 点击 "Run workflow"
4. 输入要处理的 Issue 编号
5. 查看执行日志

## 📝 测试示例

创建一个测试 Issue 来验证系统：

```markdown
## 🔧 智谱 AI 自动化测试

### 任务描述
请分析当前项目的 RAG 系统实现，并建议改进。

### 具体要求
1. 检查 backend/rag_system.py 的实现
2. 分析 backend/ai_generator.py 的错误处理
3. 建议至少 2 个具体的改进建议
4. 为其中一个改进创建实现代码

### 预期输出
- 代码分析报告
- 具体改进建议
- 实现代码片段
- 测试方法
```

然后给这个 Issue 添加 `claude-auto` 标签。

## 🔧 系统功能

### ✅ 已实现功能

- **智能分析**: 智谱 AI 分析问题并提供解决方案
- **中文支持**: 全中文提示词和回复
- **自动分类**: 根据标签自动识别问题类型
- **代码生成**: 生成具体的修复代码
- **进度追踪**: 实时在 Issue 中更新处理进度

### 🚧 待完善功能

- **自动 PR 创建**: 需要额外的 Git 操作配置
- **多文件修改**: 需要完善代码应用逻辑
- **测试验证**: 自动化测试和验证

## 📊 工作流程

```
用户创建 Issue
    ↓
添加 'claude-auto' 标签
    ↓
GitHub Actions 触发
    ↓
获取 Issue 上下文
    ↓
调用智谱 AI 分析
    ↓
生成解决方案和代码
    ↓
在 Issue 中发布结果
    ↓
人工审核和测试
    ↓
手动应用修复（当前）
```

## 💡 最佳实践

1. **清晰的 Issue 描述**: 提供详细的问题描述和环境信息
2. **适当的标签**: 使用相关标签帮助 AI 理解问题类型
3. **代码审核**: 始终审核 AI 生成的代码
4. **测试验证**: 彻底测试所有建议的修复
5. **渐进式采用**: 先在简单问题上测试系统

## 🔒 安全说明

- ✅ API Key 通过 GitHub Secrets 安全存储
- ✅ 仅授予必要的仓库权限
- ✅ 所有代码都需要人工审核
- ✅ 建议启用分支保护规则

## 📞 获取帮助

- 查看详细文档: `.github/CLAUDE_AUTOMATION.md`
- 检查 Actions 日志: GitHub Actions 页面
- 查看 Issue 评论: 智谱 AI 的回复和进度

## 💰 成本说明

- **智谱 AI**: 按用量计费，价格比 Claude 低
- **GLM-4-Flash**: 性价比高，适合日常使用
- **无订阅费**: 无需 Pro 订阅
- **按需付费**: 只为实际使用的 API 调用付费

---
