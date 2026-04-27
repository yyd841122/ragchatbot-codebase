# Zhipu AI Agent 文档导航

本文档是 Zhipu AI Agent 的统一入口，为不同使用场景提供导航。

---

## 快速导航

### 我是新用户，首次使用
→ **[快速开始](#首次使用)**：5 分钟了解核心功能（支持 .md 文件和部分配置文件）

### 我要日常使用
→ **[使用指南](#日常使用)**：完整的 Stage 1-6 操作流程

### 我遇到了问题
→ **[问题排查](#遇到问题)**：常见失败原因和解决方案

### 我要 review PR
→ **[PR Review](#review-pr)**：Draft PR 人工检查清单

### 我是开发者/维护者
→ **[开发文档](#开发维护)**：技术实现、测试记录、工作规划

---

## 首次使用

### ⚠️ 当前 MVP 限制（重要）

**在使用前，请务必了解当前系统的限制：**

- ✅ **支持根目录和一级子目录的 `.md` 文件修改**
- ✅ **支持根目录的配置文件 append-only 模式**（仅 `.gitignore`、`.env.example`）
- ❌ 不支持代码文件（`.py`、`.yml`、`.json` 等）
- ❌ 不支持多文件批量修改
- ❌ 不支持更深层的目录（路径超过 2 段，如 `docs/deep/file.md`）
- ❌ 不支持 `requirements.txt` 等其他配置文件
- ✅ 必须人工 review 后才能合并

**如果你的需求超出上述限制，当前系统无法完成。**

---

### 1. 系统能力概述

**Zhipu AI Agent** 是一个基于智谱 AI GLM-4-Flash 模型的 GitHub 自动化工具，可以：

1. **理解 Issue**：读取 GitHub Issue 的标题、正文和评论
2. **生成计划**：自动生成结构化的执行计划（Todo List）
3. **自动执行**：
   - 修改目标 `.md` 文件
   - 对配置文件（`.gitignore`、`.env.example`）执行 append-only 操作
4. **人工确认**：Draft PR 需要人工 review 后才能合并

### 2. 核心流程（6 步）

```
Issue → @zhipu → 计划生成 → /zhipu-apply → 自动修改 → Draft PR → 人工 review → 合并
 (Stage 1)                                           (Stage 2-6)
```

**触发方式**：
- **Stage 1**：在 Issue 中评论 `@zhipu`
- **Stage 2-6**：在 Issue 中评论 `/zhipu-apply`

### 3. 立即测试

**推荐测试 Issue**（Markdown 文件或配置文件）：
- **Markdown 文件测试**：
  - 标题：更新 README.md
  - 内容：描述文档修改需求
- **配置文件测试**：
  - 标题：追加 .gitignore 忽略规则
  - 内容：在 .gitignore 中追加 `*.log`

**操作步骤**：
  1. 评论 `@zhipu` → 生成计划
  2. 检查计划的第一个文件是否为支持的文件（.md 或 .gitignore/.env.example）
  3. 评论 `/zhipu-apply` → 自动执行
  4. 等待 Draft PR 创建
  5. 人工 review 并决定是否合并

---

## 日常使用

### 完整使用流程

📖 **详细文档**：[ZHIPU_AGENT_USAGE.md](ZHIPU_AGENT_USAGE.md)

#### Step 1：创建 Issue
明确说明修改目标，**当前支持 .md 文件和配置文件（.gitignore、.env.example）修改需求**

#### Step 2：生成计划
在 Issue 中评论：`@zhipu`

**重点检查**：
- `### 计划修改文件` 章节
- **第一个文件必须是 `README.md`**
- 不能使用占位路径（如 `path/to/README.md`）

#### Step 3：执行自动化
确认计划无误后，在 Issue 中评论：`/zhipu-apply`

**系统自动执行**：
- Step 1：识别触发命令
- Step 2：读取 Issue 上下文
- Step 3：创建工作分支 `zhipu/issue-{issue_number}`
- Step 4：修改 `README.md`
- Step 5：创建 commit
- Step 6：创建 Draft PR

#### Step 4：人工 Review
📖 **详细文档**：[PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md)

**检查项**：
- [ ] PR 来源正确（`/zhipu-apply` 触发）
- [ ] 只修改了 `README.md`
- [ ] 修改内容符合 Issue 需求
- [ ] 无错别字、语法错误

#### Step 5：合并
如所有检查通过：
1. 点击 "Ready for review"
2. 点击 "Merge pull request"
3. 选择 "Merge commit"

---

## 遇到问题

### 常见失败原因

📖 **详细文档**：[ZHIPU_AGENT_USAGE.md - 常见失败原因](ZHIPU_AGENT_USAGE.md#常见失败原因)

| 问题 | 常见原因 | 解决方法 |
|------|---------|---------|
| **Stage 1 计划验证失败** | 第一个文件不是 `README.md` | 重新评论 `@zhipu`，确保第一个文件是 `README.md` |
| **Step 4 文件读取失败** | 文件路径错误或文件不存在 | 确保第一个文件是真实存在的 `README.md` |
| **Step 6 创建 Draft PR 失败** | GitHub Actions/PR 权限未配置 | 联系仓库管理员确认权限配置 |
| **没有成功触发** | 评论中没有触发命令 | 确保评论包含 `@zhipu` 或 `/zhipu-apply` |

### 查看运行日志

**GitHub Actions 日志**：
1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Zhipu Issue Agent" 或 "Zhipu Issue Apply"
4. 点击具体运行记录查看日志

---

## Review PR

### Draft PR 人工 Review 清单

📖 **完整清单**：[PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md)

### 快速检查（必做项）

- [ ] PR 状态为 Draft（非 "Ready for review"）
- [ ] 分支名称格式：`zhipu/issue-{issue_number}`
- [ ] **只修改了 `README.md`**（发现其他文件立即停止）
- [ ] 修改内容符合 Issue 需求
- [ ] 无错别字、语法错误
- [ ] GitHub Actions 无失败

### 通过标准

必须全部满足：
- ✅ 只修改 `README.md`
- ✅ 修改内容符合 Issue 需求
- ✅ 无错别字、语法错误
- ✅ GitHub Actions 无失败
- ✅ 符合 MVP 限制

---

## 开发维护

### 系统架构

**技术栈**：
- GitHub Actions（工作流自动化）
- Python 3.13（脚本语言）
- Zhipu AI GLM-4-Flash（AI 模型）
- PyGithub（GitHub API 客户端）

**核心文件**：
- `.github/workflows/zhipu-agent-issue.yml` - Stage 1 工作流
- `.github/workflows/zhipu-agent-issue-apply.yml` - Stage 2-6 工作流
- `.github/scripts/agent_issue_handler.py` - Stage 1 执行脚本
- `.github/scripts/agent_issue_executor.py` - Stage 2-6 执行脚本

### 测试记录

| 阶段 | 文档 |
|------|------|
| Stage 6 完成 | [STAGE6_COMPLETE.md](STAGE6_COMPLETE.md) |
| Stage 7 Task 1 正常路径测试 | [STAGE7_TASK1_TEST_RESULT.md](STAGE7_TASK1_TEST_RESULT.md) |
| Stage 7 Task 1 异常路径测试 | [STAGE7_TASK1_EXCEPTION_TEST_RESULT.md](STAGE7_TASK1_EXCEPTION_TEST_RESULT.md) |
| Stage 8.2 完成 | [STAGE8_2_COMPLETE.md](STAGE8_2_COMPLETE.md) |
| Stage 8.3 完成 | [STAGE8_3_COMPLETE.md](STAGE8_3_COMPLETE.md) |
| Stage 8.4 Step 1 完成 | [STAGE8_4_STEP1_COMPLETE.md](STAGE8_4_STEP1_COMPLETE.md) |

### 工作规划

📖 **当前规划**：[STAGE7_PLAN.md](STAGE7_PLAN.md)

**Stage 7 目标**：
1. ✅ Task 1：改进 Stage 1 计划生成质量（已完成）
2. 待执行：文档入口整理（当前任务）
3. 可选：添加简单重试机制

---

## 附录

### 相关文档

- **[ZHIPU_AGENT_USAGE.md](ZHIPU_AGENT_USAGE.md)** - 完整使用指南
- **[PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md)** - PR Review 清单
- **[STAGE6_COMPLETE.md](STAGE6_COMPLETE.md)** - Stage 6 完成总结
- **[STAGE7_PLAN.md](STAGE7_PLAN.md)** - Stage 7 工作规划

### 快速命令参考

```bash
# 查看 PR 详情
gh pr view <pr-number>

# 查看 PR 修改的文件
gh pr diff <pr-number>

# 切换到 PR 分支
git checkout zhipu/issue-{N}
```

---

**文档维护**：@yyd841122
**最后更新**：2026-04-23
