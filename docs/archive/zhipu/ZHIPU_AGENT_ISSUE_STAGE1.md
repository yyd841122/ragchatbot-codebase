> **⚠️ 归档文档**
> 本文档已归档，内容可能过时。
> 请优先使用 [Zhipu AI Agent 文档导航](../../ZHIPU_GUIDE.md) 作为当前入口。
>
> **归档日期**：2026-04-23
> **归档原因**：第一阶段详细记录，历史开发文档，已无日常参考价值
>
> ---

# ZHIPU_AGENT_ISSUE_STAGE1

## 1. 目标

实现第一阶段的 Zhipu Issue Agent，让用户在 GitHub Issue 评论中输入 `@zhipu` 后，自动触发 GitHub Actions，读取 Issue 上下文，调用智谱 AI 生成结构化执行计划，并自动评论回当前 Issue。

本阶段只实现"计划型助手"，暂不执行改代码、建分支、提交 commit、创建 PR。

---

## 2. 本阶段已实现的能力

- 监听 GitHub Issue 评论事件
- 识别评论中是否包含 `@zhipu`
- 自动过滤 PR 评论，只处理普通 Issue
- 读取 Issue 标题、正文、最近评论
- 调用智谱 AI 生成中文结构化执行计划
- 自动将执行计划评论回对应 Issue

---

## 3. 触发方式

在 GitHub 仓库的 Issue 评论区输入：

```text
@zhipu can you make a plan for this?
```

触发后，GitHub Actions 会自动运行，并在当前 Issue 下生成类似如下结构的评论：

- 问题理解
- 计划修改文件
- Todo List
- 风险提示
- 下一步

---

## 4. 新增文件

### `.github/workflows/zhipu-agent-issue.yml`

第一阶段的 GitHub Actions workflow 文件。
负责监听 `issue_comment` 事件，并在评论包含 `@zhipu` 时触发执行。

### `.github/requirements-agent.txt`

第一阶段依赖文件。
包含智谱 SDK、PyGithub 等运行所需依赖。

### `.github/scripts/agent_issue_handler.py`

第一阶段核心处理脚本。
负责读取环境变量、连接 GitHub API、采集 Issue 上下文、调用智谱、评论回 Issue。

### `.github/scripts/test_agent_issue_local.py`

本地模拟测试脚本。
 用于在本地模拟 GitHub Actions 环境，测试 `agent_issue_handler.py` 是否能正常运行。

---

## 5. Workflow 逻辑

### 5.1 触发条件

- 事件类型：`issue_comment`
- 仅处理 `created`
- 仅处理普通 Issue
- 评论内容必须包含 `@zhipu`

### 5.2 执行流程

1. GitHub Actions 被触发
2. 安装 Python 依赖
3. 注入环境变量：
   - `GITHUB_TOKEN`
   - `ZHIPU_API_KEY`
   - `REPO`
   - `ISSUE_NUMBER`
   - `COMMENT_BODY`
   - `COMMENT_AUTHOR`
4. 执行 `agent_issue_handler.py`
5. 脚本读取 Issue 内容
6. 调用智谱生成计划
7. 自动评论回当前 Issue

---

## 6. 本地测试流程

### 6.1 语法检查

```bash
python -m py_compile .github/scripts/agent_issue_handler.py
```

### 6.2 本地模拟测试

```bash
python .github/scripts/test_agent_issue_local.py
```

本地测试时需要准备：

- 有效的 `GITHUB_TOKEN`
- 有效的 `ZHIPU_API_KEY`

并按提示输入：

- 仓库名
- Issue 编号
- 评论内容
- 评论者

---

## 7. 真实线上验证结果

本阶段已经完成真实线上验证：

- PR 已成功创建并合并到 `main`
- GitHub Actions 已在仓库默认分支生效
- 在 Issue `#3` 中真实评论 `@zhipu`
- `github-actions bot` 已成功自动回帖
- 自动回帖内容为结构化的 `Zhipu Fix Plan`

说明第一阶段已正式跑通。

---

## 8. 本阶段遇到的主要问题

### 问题 1：Python 缩进 / 代码块粘贴错乱

**原因**：

- 聊天窗口中的 Markdown 代码块与 Python 多行字符串中的反引号嵌套，导致复制后代码显示错乱

**解决**：

- 使用完整代码块一次性覆盖
- 去掉 prompt 中嵌套的 Markdown 代码围栏

---

### 问题 2：本地测试脚本导入路径错误

**报错**：

```
ModuleNotFoundError: No module named 'github.scripts'
```

**原因**：

- 把本地 `.github/scripts` 误当成 Python 包路径导入

**解决**：

```
from agent_issue_handler import main as agent_main
```

---

### 问题 3：本地测试缺少 `GITHUB_TOKEN`

**报错**：

```
环境变量 GITHUB_TOKEN 未设置
```

**解决**：

在 PowerShell 中手动设置：

```
$env:GITHUB_TOKEN="你的真实GitHubToken"
```

---

### 问题 4：GitHub API 401 Bad credentials

**原因**：

- 使用了假的 token 或无效 token

**解决**：

- 创建并使用真实可用的 GitHub Personal Access Token

---

### 问题 5：GitHub API 404 Not Found

**原因**：

- 测试输入的仓库名错误

**解决**：

改为真实仓库名：

```
yyd841122/ragchatbot-codebase
```

---

### 问题 6：GitHub API 403 Resource not accessible by personal access token

**原因**：

- token 权限不足，无法写 Issue 评论

**解决**：

- 使用新的 classic token
- 确保具备 `repo` 权限

---

## 9. 当前功能边界

本阶段**尚未实现**：

- `/zhipu-apply`
- 自动改代码
- 自动建分支
- 自动 commit
- 自动创建 PR

所以当前系统属于：

**Issue 计划型 AI 助手**

而不是执行型代理。

---

## 10. 第二阶段目标

下一阶段准备实现：

```
/zhipu-apply
```

目标能力：

- 在 Issue 中输入 `/zhipu-apply`
- 自动创建工作分支
- 自动修改代码
- 自动运行检查
- 自动提交 commit
- 自动创建 Draft PR

也就是从"计划型助手"升级为"执行型代理"。

---

## 11. 当前结论

第一阶段已经正式完成并验证通过。

仓库现在已经具备基于 GitHub Issue 评论触发的 Zhipu AI 计划生成能力。
