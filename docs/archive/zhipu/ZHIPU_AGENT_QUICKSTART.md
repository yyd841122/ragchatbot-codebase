> **⚠️ 归档文档**
> 本文档已归档，内容可能过时。
> 请优先使用 [Zhipu AI Agent 文档导航](../../ZHIPU_GUIDE.md) 作为当前入口。
>
> **归档日期**：2026-04-23
> **归档原因**：快速启动指南，内容已整合到 ZHIPU_GUIDE.md
>
> ---

# 🚀 Zhipu Issue Agent - 快速启动

## ✅ 验证结果

```
🎉 所有检查通过！
```

所有必需的文件已创建，配置正确。

---

## 📦 已创建的文件

### 核心文件（3 个）

1. **`.github/workflows/zhipu-agent-issue.yml`**
   - GitHub Actions 工作流配置
   - 监听 Issue 评论，触发 Agent

2. **`.github/requirements-agent.txt`**
   - Python 依赖列表
   - 包含 zhipuai、PyGithub 等

3. **`.github/scripts/agent_issue_handler.py`**
   - 核心执行脚本
   - 读取 Issue → 调用智谱 AI → 回复评论

### 辅助文件（3 个）

4. **`.github/scripts/test_agent_issue_local.py`**
   - 本地测试脚本
   - 模拟 GitHub Actions 环境

5. **`.github/scripts/verify_agent_setup.sh`**
   - 配置验证脚本
   - 检查所有文件和环境

6. **`.github/ISSUE_TEMPLATE/zhipu_agent_test.md`**
   - Issue 测试模板
   - 快速创建测试 Issue

---

## 🎯 立即测试

### 方法 1: 在 GitHub 上测试（推荐）

1. **提交代码到 GitHub**
   ```bash
   git add .github/
   git commit -m "feat: add Zhipu Issue Agent (phase 1)"
   git push
   ```

2. **在 GitHub 上配置 Secret**
   - 进入仓库 Settings → Secrets and variables → Actions
   - 添加 `ZHIPU_API_KEY`（值为你的智谱 API Key）

3. **创建测试 Issue**
   - 使用模板 `[TEST] Zhipu Agent 测试`
   - 或在任意 Issue 中评论 `@zhipu`

4. **等待响应**
   - 1-2 分钟后自动生成执行计划
   - 在 Actions 标签页查看运行日志

---

### 方法 2: 本地测试

```bash
# 运行本地测试脚本
python .github/scripts/test_agent_issue_local.py

# 按提示输入测试信息
# 仓库: yyd841122/starting-ragchatbot
# Issue 编号: 1
# 评论内容: @zhipu
# 评论者: test-user
```

---

## 📖 使用说明

### 触发条件

在 **Issue**（不是 PR）中评论包含以下内容：

```
@zhipu
```

或

```
@zhipu 请帮我分析这个问题
```

### 输出格式

Agent 会生成以下结构化的计划：

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

## 🔍 调试与监控

### 查看 Actions 运行日志

```
GitHub 仓库 → Actions 标签 → Zhipu Issue Agent → 点击运行记录
```

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 没有触发 | 检查评论是否包含 `@zhipu`，确认是 Issue 不是 PR |
| 提示 ZHIPU_API_KEY 未设置 | 在 GitHub Secrets 中添加 `ZHIPU_API_KEY` |
| AI 回复质量不好 | 在 Issue 中提供更多上下文信息 |

---

## 📚 文档索引

- **详细文档**: `ZHIPU_AGENT_ISSUE.md`
- **验证脚本**: `.github/scripts/verify_agent_setup.sh`
- **本地测试**: `.github/scripts/test_agent_issue_local.py`
- **Issue 模板**: `.github/ISSUE_TEMPLATE/zhipu_agent_test.md`

---

## 🎉 下一步

### 第一阶段（当前）✅

- ✅ 读取 Issue 上下文
- ✅ 调用智谱 AI 生成计划
- ✅ 自动评论回复

### 第二阶段（待实现）

- ⏳ 自动创建分支
- ⏳ 自动修改代码
- ⏳ 自动提交 commit
- ⏳ 自动创建 PR

触发方式：`/zhipu-apply`（已预留接口）

---

**准备好了吗？** 🚀

```bash
# 提交代码并测试
git add .github/
git commit -m "feat: add Zhipu Issue Agent (phase 1)"
git push
```

然后在 GitHub 上创建一个 Issue，评论 `@zhipu`，看看效果吧！
