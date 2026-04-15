# Claude AI 自动化系统快速测试指南

## 🚀 快速开始

### 1. 运行设置脚本

**Windows:**
```bash
setup_automation.bat
```

**Linux/Mac:**
```bash
bash setup_automation.sh
```

### 2. 手动设置（如果脚本失败）

#### A. 获取 Anthropic API Key
1. 访问 https://console.anthropic.com
2. 创建 API Key
3. 复制 key

#### B. 设置 GitHub Secrets
```bash
# 使用 GitHub CLI 设置
gh secret set ANTHROPIC_API_KEY --repo yyd841122/ragchatbot-codebase
# 粘贴你的 API Key

# 验证设置
gh secret list --repo yyd841122/ragchatbot-codebase
```

#### C. 推送工作流文件
```bash
git add .github/
git commit -m "Add Claude AI automation"
git push origin main
```

## 🧪 测试系统

### 测试方式 1: 自动触发（推荐）

1. 在 GitHub 创建新 Issue
2. 添加标签 `claude-auto`
3. 等待 Claude AI 处理
4. 查看 Issue 中的 AI 回复

### 测试方式 2: 手动触发

1. 访问 GitHub Actions 页面
2. 选择 "Claude AI Issue Handler"
3. 点击 "Run workflow"
4. 输入 Issue 编号
5. 查看执行日志

### 测试示例 Issue

创建这个 Issue 来测试系统：

```markdown
## 🔧 Claude AI 功能测试

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

## 📊 监控执行

### 查看工作流状态
```bash
# 列出最近的工作流运行
gh run list --repo yyd841122/ragchatbot-codebase

# 查看特定运行的日志
gh run view <run-id> --repo yyd841122/ragchatbot-codebase --log

# 监控运行中的工作流
gh run watch --repo yyd841122/ragchatbot-codebase
```

### 查看 AI 处理进度
Claude AI 会在 Issue 中发布评论更新：
1. 初始分析
2. 解决方案设计
3. 代码生成进度
4. PR 创建状态

## 🎯 不同类型的 Issue 测试

### Bug 修复测试
```markdown
## 🐛 Bug: 查询超时

### 问题描述
当查询包含大量数据时，系统会超时。

### 错误日志
```
TimeoutError: Request took too long to complete
```

### 重现步骤
1. 搜索包含 "machine learning" 的内容
2. 等待响应
3. 出现超时错误
```

### 功能增强测试
```markdown
## ✨ 增强: 添加搜索历史

### 需求描述
希望系统能够记住用户的搜索历史，并提供历史记录查询功能。

### 期望功能
- 保存最近 100 条搜索
- 按时间排序显示
- 支持删除历史记录
```

### 文档改进测试
```markdown
## 📚 文档: API 使用说明

### 需要改进
当前的 API 文档缺少使用示例和参数说明。

### 要求
1. 添加每个端点的详细说明
2. 提供请求/响应示例
3. 添加错误处理说明
4. 补充认证方法
```

## 🔧 故障排除

### 问题: 工作流没有运行
**解决:**
```bash
# 检查工作流文件语法
yamllint .github/workflows/claude-issue-handler.yml

# 验证 GitHub Actions 权限
gh api repos/yyd841122/ragchatbot-codebase/actions/permissions
```

### 问题: Claude API 错误
**解决:**
```bash
# 验证 API Key
gh secret view ANTHROPIC_API_KEY --repo yyd841122/ragchatbot-codebase

# 检查 API 配额
curl https://console.anthropic.com/settings/usage
```

### 问题: 没有创建 PR
**解决:**
- 检查 Issue 是否有 `claude-auto` 标签
- 查看 GitHub Actions 日志
- 验证仓库权限设置

## 📈 性能优化建议

1. **批量处理**: 一次处理多个相关 Issues
2. **优先级设置**: 使用标签标记优先级
3. **模板标准化**: 为常见问题创建 Issue 模板
4. **结果缓存**: 缓存 Claude API 响应

## 🎓 高级用法

### 自定义 Claude 提示词
编辑 `.github/scripts/claude_issue_handler.py`:
```python
prompt = f"""
你的自定义提示词...
"""
```

### 添加新的处理步骤
在工作流文件中添加新的步骤:
```yaml
- name: Custom processing step
  run: |
    # 你的自定义处理逻辑
```

### 集成其他工具
- 添加 Slack 通知
- 集成测试工具
- 连接项目管理工具

## 📞 获取帮助

- 查看详细文档: `.github/CLAUDE_AUTOMATION.md`
- 检查 Actions 日志: GitHub Actions 页面
- 查看 Issue 评论: Claude AI 的回复

---

**提示**: 这个系统是实验性的，始终审核和测试自动生成的代码！