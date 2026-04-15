# Claude AI 自动化 Issue 处理系统

这个系统使用 Claude AI 自动分析 GitHub Issues 并生成修复代码。

## 🚀 功能特性

- **智能分析**: Claude AI 分析问题并提供解决方案
- **自动修复**: 自动生成代码变更
- **Pull Request**: 自动创建 PR 应用修复
- **问题分类**: 自动标记和分类 issues
- **进度追踪**: 实时更新处理进度

## 📋 前置要求

1. **Anthropic API Key**: 从 https://console.anthropic.com 获取
2. **GitHub Repository**: 仓库必须启用 GitHub Actions
3. **权限设置**: GitHub Actions 需要 `contents`, `issues`, `pull-requests` 权限

## 🔧 安装步骤

### 1. 配置 GitHub Secrets

在你的 GitHub 仓库中添加以下 secrets:

1. 访问 `https://github.com/yyd841122/ragchatbot-codebase/settings/secrets/actions`
2. 添加以下 secrets:

   - **ANTHROPIC_API_KEY**: 你的 Anthropic API 密钥

### 2. 使用方式

#### 方式 A: 自动触发（推荐）

给 Issue 添加 `claude-auto` 标签，Claude AI 将自动处理:

```bash
# 在 GitHub Issue 中添加标签 "claude-auto"
```

#### 方式 B: 手动触发

1. 访问 GitHub Actions 页面
2. 选择 "Claude AI Issue Handler" 工作流
3. 点击 "Run workflow"
4. 输入要处理的 Issue 编号

### 3. 工作流程

1. **Issue 创建**: 用户创建新 Issue
2. **标签标记**: 添加 `claude-auto` 标签
3. **自动分析**: Claude AI 分析问题
4. **生成修复**: 自动生成代码修复
5. **创建 PR**: 自动创建 Pull Request
6. **人工审核**: 团队审核和测试

## 📝 Issue 模板

为了获得最佳效果，创建 Issue 时请包含以下信息:

```markdown
### 问题描述
[详细描述遇到的问题]

### 预期行为
[描述预期的正常行为]

### 实际行为
[描述实际发生的错误行为]

### 重现步骤
1. 第一步
2. 第二步
3. 第三步

### 环境信息
- 操作系统: [Windows/Mac/Linux]
- Python 版本: [3.13]
- 其他相关信息: [...]

### 日志/错误信息
```
[相关错误日志或堆栈跟踪]
```
```

## 🤖 Claude AI 处理流程

Claude AI 会执行以下步骤:

1. **问题分析**: 理解问题的根本原因
2. **方案设计**: 设计最合适的解决方案
3. **代码生成**: 生成具体的代码修改
4. **测试建议**: 提供测试和验证方法
5. **PR 创建**: 自动创建 Pull Request

## 📊 监控和日志

- **GitHub Actions**: 查看工作流执行日志
- **Issue Comments**: Claude AI 会在 Issue 中更新进度
- **Pull Requests**: 自动生成的 PR 包含详细说明

## ⚙️ 自定义配置

### 修改 Claude 模型

编辑 `.github/workflows/claude-issue-handler.yml`:

```yaml
- name: Process Issue with Claude
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    CLAUDE_MODEL: claude-sonnet-4-6  # 修改模型
```

### 调整触发条件

编辑 `.github/workflows/claude-issue-handler.yml`:

```yaml
on:
  issues:
    types: [opened, reopened]  # 修改触发事件
  issue_comment:
    types: [created]
```

## 🔒 安全考虑

- **API Key**: 通过 GitHub Secrets 安全存储
- **权限限制**: 仅授予必要的仓库权限
- **代码审核**: 所有自动生成的代码都需要人工审核
- **分支保护**: 建议启用分支保护规则

## 🐛 故障排除

### 问题: 工作流没有触发

**解决方案:**
- 检查是否添加了 `claude-auto` 标签
- 验证 GitHub Actions 权限设置
- 查看 Actions 日志获取错误信息

### 问题: Claude API 调用失败

**解决方案:**
- 验证 ANTHROPIC_API_KEY 是否正确
- 检查 API 配额和限制
- 查看 Actions 日志中的详细错误

### 问题: 无法创建 Pull Request

**解决方案:**
- 确保仓库有适当权限
- 检查分支保护规则
- 验证 GITHUB_TOKEN 权限

## 📈 最佳实践

1. **清晰的 Issue 描述**: 提供详细的问题描述
2. **适当的标签**: 使用相关标签帮助 Claude AI 理解问题
3. **代码审核**: 始终审核自动生成的代码
4. **测试验证**: 彻底测试所有自动修复
5. **渐进式采用**: 先在简单问题上测试系统

## 🎯 高级特性

### 批量处理 Issues

可以批量触发多个 Issues 的处理:

```bash
# 使用 GitHub CLI
gh issue list --label "bug" --json number --jq '.[].number' | \
  xargs -I {} gh workflow run claude-issue-handler.yml -f issue_number={}
```

### 自定义分析提示

修改 `.github/scripts/claude_issue_handler.py` 中的提示词以获得更好的结果:

```python
prompt = f"""自定义你的提示词..."""
```

## 📞 支持

如有问题，请:
1. 查看 GitHub Actions 日志
2. 检查 Issue 中的 Claude AI 评论
3. 参考本文档的故障排除部分

---

**注意**: 这个系统是实验性的，生成的代码需要人工审核和测试。