> **⚠️ 归档文档**
> 本文档已归档，内容可能过时。
> 请优先使用 [Zhipu AI Agent 文档导航](../../ZHIPU_GUIDE.md) 作为当前入口。
>
> **归档日期**：2026-04-23
> **归档原因**：第一阶段完整说明，部分内容已过时，已被 ZHIPU_AGENT_USAGE.md 取代
>
> ---

# Zhipu Issue Agent - 第一阶段实现

## 📋 功能说明

本阶段实现了一个"计划型助手"，当用户在 GitHub Issue 中评论 `@zhipu` 时，系统会：

1. 自动读取 Issue 的标题、正文和评论历史
2. 调用智谱 AI 生成结构化的执行计划（Todo List）
3. 将计划自动评论回 Issue

**注意**：本阶段只生成计划，不执行实际的代码修改。

---

## 🚀 快速开始

### 1. 确认 GitHub Secrets

确保你的仓库中已经配置了以下 Secrets：

**必需的 Secrets**：
- `ZHIPU_API_KEY` - 智谱 AI 的 API Key

**自动提供的 Secrets**（无需配置）：
- `GITHUB_TOKEN` - GitHub 自动提供

### 2. 测试 Agent

在任意 Issue 中评论：

```
@zhipu
```

然后等待 1-2 分钟，GitHub Actions 会自动触发并生成回复。

---

## 📁 文件结构

```
.github/
├── workflows/
│   └── zhipu-agent-issue.yml      # GitHub Actions 工作流
├── requirements-agent.txt          # Python 依赖
└── scripts/
    └── agent_issue_handler.py      # 执行脚本（核心逻辑）
```

---

## 🔧 工作原理

### 触发条件

- **事件**：`issue_comment`（创建评论时）
- **条件**：
  - 评论内容包含 `@zhipu`
  - 是 Issue 评论，不是 PR 评论

### 执行流程

```
用户评论 @zhipu
    ↓
GitHub Actions 触发
    ↓
读取 Issue 上下文
    ↓
调用智谱 AI (glm-4-flash)
    ↓
生成结构化计划
    ↓
自动评论回 Issue
```

---

## 📝 输出格式

智谱 AI 会生成以下格式的回复：

```markdown
## 🤖 Zhipu Fix Plan

### 问题理解
[简洁总结]

### 计划修改文件
- `path/to/file1` - [修改目的]
- `path/to/file2` - [修改目的]

### Todo List
- [ ] [步骤1] - [预期结果]
- [ ] [步骤2] - [预期结果]
- [ ] [步骤3] - [预期结果]
- [ ] [步骤4] - [预期结果]
- [ ] [步骤5] - [预期结果]

### 风险提示
- [风险点1]
- [风险点2]

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）
```

---

## 🧪 本地测试

如果想在本地测试脚本（不推送到 GitHub）：

```bash
# 设置环境变量
export GITHUB_TOKEN="your_github_token"
export ZHIPU_API_KEY="your_zhipu_api_key"
export REPO="owner/repo"
export ISSUE_NUMBER="123"
export COMMENT_BODY="@zhipu 请帮我分析这个问题"
export COMMENT_AUTHOR="your_username"

# 运行脚本
python .github/scripts/agent_issue_handler.py
```

---

## 🔍 调试与监控

### 查看 Actions 运行日志

1. 进入仓库的 "Actions" 标签页
2. 选择 "Zhipu Issue Agent" 工作流
3. 点击具体的运行记录查看日志

### 常见问题

**Q: 没有触发怎么办？**
- 检查评论是否包含 `@zhipu`
- 确认是 Issue 而不是 PR
- 查看 Actions 标签页是否有运行记录

**Q: 提示 ZHIPU_API_KEY 未设置？**
- 前往仓库 Settings → Secrets and variables → Actions
- 添加 `ZHIPU_API_KEY`

**Q: AI 生成的计划质量不好？**
- 可以在 Issue 中提供更多上下文信息
- 在评论中明确提出需求，例如：`@zhipu 请重点关注性能优化`

---

## 📊 依赖说明

`.github/requirements-agent.txt`：

```
zhipuai>=2.1.0      # 智谱 AI SDK
PyGithub>=2.3.0     # GitHub API SDK
sniffio>=1.3.1      # 异步 I/O 依赖
requests>=2.31.0    # HTTP 库
```

---

## 🎯 下一步（第二阶段预览）

第二阶段将实现真正的自动化执行：

- ✅ 自动创建分支
- ✅ 自动修改代码
- ✅ 自动提交 commit
- ✅ 自动创建 Pull Request

触发方式：评论 `/zhipu-apply`（本阶段已预留提示）

---

## 📚 相关文档

- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyGithub 文档](https://pygithub.readthedocs.io/)
