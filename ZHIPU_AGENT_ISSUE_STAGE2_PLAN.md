# ZHIPU_AGENT_ISSUE_STAGE2_PLAN

## 1. 第二阶段目标

### 1.1 与第一阶段的区别

**第一阶段（已实现）：计划型助手**
- 用户在 Issue 评论 `@zhipu`
- 系统读取 Issue 上下文
- 调用智谱 AI 生成结构化执行计划
- 自动评论回 Issue，展示计划
- **不执行任何代码修改**

**第二阶段（本阶段）：执行型代理**
- 用户在 Issue 评论 `/zhipu-apply`
- 系统进入"执行模式"，实际进行代码修改
- 自动创建工作分支
- 自动生成或修改代码
- 自动运行检查
- 自动提交 commit
- 自动创建 Draft PR
- **真正完成从计划到落地的闭环**

### 1.2 核心价值

从"给你一个计划"升级为"帮你把事做完"，减少开发者手动执行 Todo List 的时间成本。

---

## 2. 预期触发方式

### 2.1 触发命令

在 Issue 评论区输入：

```
/zhipu-apply
```

### 2.2 与 `@zhipu` 的关系

- **独立触发**：`/zhipu-apply` 是独立的命令，不需要先执行 `@zhipu`
- **建议工作流**：用户可以先 `@zhipu` 查看计划，确认后再 `/zhipu-apply` 执行
- **但允许直接执行**：如果用户直接输入 `/zhipu-apply`，系统会在内部先生成计划再执行

### 2.3 触发范围限制

- **仅限普通 Issue**：不处理 PR 评论（与第一阶段保持一致）
- **仅限仓库成员**：建议只允许 repository owner 或 collaborator 触发
- **不限制分支**：可以在默认分支或保护分支上触发

### 2.4 权限校验

在 workflow 中检查：

```yaml
if: >
  github.event.issue.pull_request == null &&
  contains(github.event.comment.body, '/zhipu-apply') &&
  (github.event.comment.user.login == 'yyd841122' ||
   github.event.author_association == 'OWNER' ||
   github.event.author_association == 'COLLABORATOR' ||
   github.event.author_association == 'MEMBER')
```

---

## 3. 第二阶段整体流程

### 3.1 文字版流程图

```
1. 用户在 Issue 评论 /zhipu-apply
   ↓
2. GitHub Actions workflow 触发
   ↓
3. 环境变量注入
   - GITHUB_TOKEN
   - ZHIPU_API_KEY
   - ISSUE_NUMBER
   - COMMENT_BODY
   ↓
4. 执行 agent_issue_executor.py
   ↓
5. 读取 Issue 上下文
   - Issue 标题
   - Issue 正文
   - 最近评论
   - 查找是否已有 Zhipu Fix Plan
   ↓
6. 如果已有计划：直接使用
   如果没有计划：先调用 AI 生成计划
   ↓
7. 将计划拆解为可执行的步骤
   ↓
8. 创建工作分支
   - 分支命名：zhipu/issue-{issue_number}-{timestamp}
   ↓
9. 调用 AI 生成代码修改
   - 读取现有文件内容
   - 生成修改后的完整内容
   ↓
10. 执行文件修改
   - 使用 git 操作：checkout → 写入文件
   ↓
11. 运行检查（MVP 可选）
   - 语法检查：python -m py_compile
   ↓
12. 提交 commit
   - commit message 模板：fix issue#{issue_number}: {title}
   ↓
13. git push 到远程
   ↓
14. 创建 Draft PR
   - 标题：[Zhipu AI] Issue #{issue_number}: {title}
   - 正文：包含执行步骤、修改文件、风险提示
   ↓
15. 在 Issue 评论执行结果
   - 执行状态：✅ 成功 / ❌ 失败
   - 创建的分支名
   - PR 链接（如果成功）
   - 错误信息（如果失败）
   ↓
16. 结束
```

### 3.2 失败回滚策略

- **在 push 前失败**：删除本地分支，不创建远程分支，只在 Issue 评论错误信息
- **在 push 后失败**：保留远程分支，在 Issue 评论错误信息和手动处理建议

---

## 4. 建议新增文件

### 4.1 核心文件

#### `.github/workflows/zhipu-agent-issue-apply.yml`（新增）

**职责**：第二阶段的 GitHub Actions workflow

**与第一阶段的关系**：
- 与 `zhipu-agent-issue.yml` 并列，不是替换
- 两个 workflow 可以共存，分别响应不同触发词

**关键配置**：
```yaml
on:
  issue_comment:
    types: [created]

permissions:
  contents: write  # 需要写权限，用于 push 和 PR
  issues: write
  pull-requests: write
```

#### `.github/scripts/agent_issue_executor.py`（新增）

**职责**：第二阶段的核心执行脚本

**主要功能**：
- 读取 Issue 上下文
- 调用智谱 AI 生成代码修改
- 执行 git 操作（checkout branch, commit, push）
- 创建 PR
- 回帖执行结果

**与第一阶段的关系**：
- 可以复用 `agent_issue_handler.py` 中的部分函数（如 `get_recent_comments`、`build_context_prompt`）
- 或者直接 `import agent_issue_handler` 作为模块复用

### 4.2 支持文件

#### `.github/scripts/git_operations.py`（新增）

**职责**：封装 Git 操作的工具函数

**功能**：
- `create_branch(repo, branch_name)` - 创建新分支
- `update_file(repo, branch, file_path, content, commit_message)` - 修改文件
- `commit_and_push(repo, branch, commit_message)` - 提交并推送
- `create_draft_pr(repo, branch, title, body)` - 创建 Draft PR

**优势**：
- 将 Git 操作从主脚本中分离
- 便于单独测试
- 复用性高

#### `.github/scripts/agent_issue_executor_test.py`（新增）

**职责**：本地测试脚本，模拟第二阶段执行

**与第一阶段测试脚本的关系**：
- 类似 `test_agent_issue_local.py` 的设计
- 额外模拟 git 操作

### 4.3 Prompt 模板

#### `.github/prompts/executor_prompt.md`（新增）

**职责**：存储用于生成代码修改的 prompt 模板

**内容**：
- 角色设定
- 输出格式要求
- 代码修改规则
- 安全约束

**优势**：
- prompt 与代码分离
- 便于迭代优化
- 支持版本管理

### 4.4 配置文件

#### `.github/config/executor_config.yaml`（新增）

**职责**：执行代理的配置

**内容**：
```yaml
# 分支命名规则
branch_pattern: "zhipu/issue-{issue_number}-{timestamp}"

# commit message 模板
commit_message_template: "fix issue#{issue_number}: {issue_title}"

# 默认基准分支
default_base_branch: "main"

# 单次修改文件数量限制
max_files_per_execution: 5

# 允许修改的文件类型
allowed_file_extensions:
  - .py
  - .md
  - .txt
  - .yml
  - .yaml
```

### 4.5 文档文件

#### `ZHIPU_AGENT_ISSUE_STAGE2_MVP.md`（新增）

**职责**：第二阶段 MVP 的具体实现说明

#### `ZHIPU_AGENT_ISSUE_STAGE2_TEST.md`（新增）

**职责**：第二阶段的测试用例和验证步骤

### 4.6 文件复用与扩展

#### 需要扩展的现有文件

**`.github/requirements-agent.txt`**：

新增依赖：
```
GitPython>=3.1.40  # 用于 Python 内的 git 操作
```

---

## 5. 第二阶段最小可行版本（MVP）

### 5.1 MVP 范围定义

**核心目标**：先跑通"从 Issue 到 PR"的完整链路

### 5.2 MVP 限制

#### 5.2.1 功能限制

- **仅支持单文件修改**：一次执行只修改 1 个文件
- **仅支持 Python 文件**：暂不支持其他语言
- **仅支持简单修改**：不涉及复杂重构或多文件联动
- **不支持多轮修复**：如果第一次修改失败，不自动重试
- **不支持冲突处理**：如果遇到 git 冲突，直接报错

#### 5.2.2 安全限制

- **必须白名单**：只能修改 `allowed_file_extensions` 中的文件类型
- **必须先展示计划**：AI 在修改代码前，先在日志中输出"即将修改的文件和原因"
- **必须语法检查**：修改后运行 `python -m py_compile`，语法不通过则不提交
- **必须有大小限制**：单次修改的代码行数不超过 100 行

#### 5.2.3 Git 限制

- **只创建 Draft PR**：不直接创建可合并的 PR
- **只提交一次 commit**：不进行多次 commit
- **不做 push force**：避免覆盖已有提交

### 5.3 MVP 不包含的内容

- ❌ 自动运行测试（pytest）
- ❌ 自动修复 lint 错误
- ❌ 多文件批量修改
- ❌ 自动合并 PR
- ❌ 处理 git 冲突
- ❌ 回滚机制
- ❌ 代码审查功能

### 5.4 MVP 成功标准

1. 用户在 Issue 评论 `/zhipu-apply`
2. 系统成功创建分支
3. 系统成功修改 1 个 Python 文件
4. 系统成功创建 Draft PR
5. Issue 评论包含 PR 链接
6. 代码能够正常运行（无语法错误）

---

## 6. 关键风险点

### 6.1 AI 改错代码

**风险描述**：AI 生成的代码有逻辑错误或安全隐患

**影响**：
- 引入新 bug
- 安全漏洞
- 性能下降

**缓解措施**：
- 使用 Draft PR，不直接合并
- 在 PR 正文中标注"AI 生成，请人工审查"
- 在 Issue 评论中明确提示"需要人工 review"
- MVP 只做语法检查，不做逻辑验证

### 6.2 修改范围过大

**风险描述**：AI 一次性修改大量文件或代码

**影响**：
- 难以 review
- 难以回滚
- 可能误改无关文件

**缓解措施**：
- 配置 `max_files_per_execution = 1`（MVP）
- 配置 `max_lines_per_change = 100`（MVP）
- 文件类型白名单
- 在执行前输出"即将修改的文件列表"，方便人工 review

### 6.3 误改无关文件

**风险描述**：AI 修改了不应该修改的文件

**影响**：
- 破坏无关功能
- 配置文件被改坏
- 敏感文件泄漏

**缓解措施**：
- 文件类型白名单（`.py`, `.md` 等）
- 目录黑名单（如 `.github/`, `node_modules/`）
- 文件大小限制（如最大 100KB）
- 关键文件保护（如 `config.py`, `.env`）

### 6.4 Git Push / PR 创建失败

**风险描述**：网络问题或权限问题导致 push 或 PR 创建失败

**影响**：
- 分支已创建但 push 失败
- 代码已提交但 PR 创建失败
- 无法在 Issue 反馈正确状态

**缓解措施**：
- 每个 Git 操作后检查返回值
- 失败时在 Issue 评论详细错误信息
- 失败时清理已创建的远程分支（避免残留）
- 提供"手动处理建议"

### 6.5 Token 权限不足

**风险描述**：GitHub Token 没有足够权限执行某些操作

**影响**：
- 无法 push 代码
- 无法创建 PR
- 无法写入 Issue 评论

**缓解措施**：
- 在 workflow 中明确声明所需权限：
  ```yaml
  permissions:
    contents: write
    issues: write
    pull-requests: write
  ```
- 在启动时检查权限
- 权限不足时在 Issue 评论明确提示

### 6.6 Workflow 权限风险

**风险描述**：如果 workflow 被滥用，可能造成仓库破坏

**影响**：
- 恶意用户大量创建垃圾分支和 PR
- 污染 git 历史
- 消耗 GitHub Actions 配额

**缓解措施**：
- 限制触发人：只允许 owner/collaborator/member
- 添加频率限制：同一 Issue 10 分钟内只能触发一次
- 添加操作确认：先评论"即将执行..."，5 秒后执行（可通过 `/zhipu-confirm` 取消）
- 添加审计日志：每次执行都在 Issue 留下记录

### 6.7 重复触发

**风险描述**：用户多次输入 `/zhipu-apply`，导致并发执行

**影响**：
- 多个 workflow 同时运行
- 可能创建多个分支和 PR
- 可能相互冲突

**缓解措施**：
- 在 Issue 中检查是否已有由 Zhipu 创建的 PR
- 如果已有 PR，拒绝再次执行
- 添加频率限制

### 6.8 并发执行

**风险描述**：多个 Issue 同时触发 `/zhipu-apply`

**影响**：
- 多个 workflow 同时运行
- 可能超出 GitHub Actions 并发限制
- 可能相互干扰

**缓解措施**：
- GitHub Actions 默认有并发限制
- 每个 workflow 独立运行，互不影响
- 如果必要，可添加 `concurrency` 控制

### 6.9 安全性问题

**风险描述**：AI 生成的代码包含恶意内容

**影响**：
- 注入恶意代码
- 泄漏敏感信息
- 破坏系统安全

**缓解措施**：
- Draft PR 必须人工 review 后才能合并
- 在 PR 正文中添加显著警告
- 限制 AI 能访问的文件（不读取 `.env`、`secrets/` 等）
- Prompt 中明确禁止生成恶意代码

### 6.10 API 失败

**风险描述**：智谱 AI API 调用失败

**影响**：
- 无法生成代码
- 无法完成执行
- 浪费 GitHub Actions 配额

**缓解措施**：
- API 调用添加重试机制（最多 3 次）
- 失败时在 Issue 评论详细错误信息
- 提供"降级方案"：至少生成计划，不执行代码修改

---

## 7. 安全与权限设计建议

### 7.1 GitHub Token 权限

**必需权限**：

```yaml
permissions:
  contents: write      # 读写代码（分支、提交、PR）
  issues: write        # 读写 Issue 评论
  pull-requests: write # 创建和管理 PR
```

**不需要的权限**：
- `workflows`: 不需要修改 workflow 文件
- `admin`: 不需要管理权限
- `deployments`: 不需要部署权限

### 7.2 触发人限制

**推荐方案**：只允许仓库成员触发

```yaml
if: >
  github.event.issue.pull_request == null &&
  contains(github.event.comment.body, '/zhipu-apply') &&
  (github.event.comment.author_association == 'OWNER' ||
   github.event.author_association == 'COLLABORATOR' ||
   github.event.author_association == 'MEMBER')
```

**原因**：
- 防止陌生用户滥用
- 保护仓库安全
- 避免垃圾分支和 PR

### 7.3 分支策略限制

**建议**：只在默认分支上执行

```yaml
if: >
  github.event.issue.pull_request == null &&
  contains(github.event.comment.body, '/zhipu-apply') &&
  github.ref == 'refs/heads/main'
```

**原因**：
- 避免在功能分支上执行导致混乱
- 保持代码库整洁

### 7.4 Dry-Run 模式

**建议**：添加 `/zhipu-apply-dry-run` 命令

**功能**：
- 只生成计划和代码，不实际执行
- 在 Issue 评论"即将执行的内容"
- 方便用户预览

**实现方式**：
```yaml
if: >
  contains(github.event.comment.body, '/zhipu-apply-dry-run')

# 在脚本中设置 dry-run 模式
os.environ["DRY_RUN"] = "true"
```

### 7.5 执行前确认机制

**建议**：两阶段执行

**流程**：
1. 用户输入 `/zhipu-apply`
2. 系统在 Issue 评论"即将执行以下操作..."，并列出：
   - 将创建的分支名
   - 将修改的文件列表
   - 将修改的内容摘要
3. 用户回复 `/zhipu-confirm` 确认
4. 系统执行实际操作

**优点**：
- 给用户反悔机会
- 减少误操作
- 提高透明度

**缺点**：
- 增加交互复杂度
- 延长执行时间

**建议**：MVP 不实现，后续阶段可选

---

## 8. 第二阶段建议分步实施顺序

### Step 1：基础框架搭建（1-2 天）

**目标**：建立 `/zhipu-apply` 触发机制

**任务**：
- 创建 `.github/workflows/zhipu-agent-issue-apply.yml`
- 创建 `.github/scripts/agent_issue_executor.py`（空实现）
- 验证触发机制：输入 `/zhipu-apply` 后 workflow 成功运行
- 验证权限配置：workflow 有 `contents: write` 权限
- 验证触发人限制：非 member 无法触发

**验收标准**：
- 在 Issue 评论 `/zhipu-apply`
- GitHub Actions 成功运行
- Issue 收到"执行中"评论

### Step 2：读取 Issue 和生成计划（1-2 天）

**目标**：复用第一阶段的计划生成逻辑

**任务**：
- 在 `agent_issue_executor.py` 中读取 Issue 上下文
- 复用 `agent_issue_handler.py` 的函数，或复制相关逻辑
- 调用智谱 AI 生成执行计划
- 在 Issue 评论"执行计划"

**验收标准**：
- `/zhipu-apply` 能生成计划
- 计划内容与 `@zhipu` 一致

### Step 3：创建分支（1 天）

**目标**：自动创建工作分支

**任务**：
- 创建 `.github/scripts/git_operations.py`
- 实现 `create_branch()` 函数
- 在 `agent_issue_executor.py` 中调用
- 分支命名规则：`zhipu/issue-{issue_number}-{timestamp}`

**验收标准**：
- 触发 `/zhipu-apply` 后，远程仓库出现新分支
- Issue 评论包含分支名

### Step 4：文件修改与 Git 操作（2-3 天）

**目标**：自动修改文件并提交

**任务**：
- 在 `git_operations.py` 中实现 `update_file()` 和 `commit_and_push()`
- 在 `agent_issue_executor.py` 中：
  - 调用 AI 生成代码修改（先硬编码一个简单例子）
  - 写入文件
  - 提交 commit
  - push 到远程
- MVP 限制：只修改 1 个文件，只修改 10 行代码

**验收标准**：
- 触发 `/zhipu-apply` 后，目标文件被修改
- commit message 格式正确
- 远程分支有新提交

### Step 5：创建 Draft PR（1 天）

**目标**：自动创建 Draft PR

**任务**：
- 在 `git_operations.py` 中实现 `create_draft_pr()`
- PR 标题：`[Zhipu AI] Issue #{issue_number}: {title}`
- PR 正文：包含执行步骤、修改文件、风险提示

**验收标准**：
- 触发 `/zhipu-apply` 后，远程仓库出现 Draft PR
- Issue 评论包含 PR 链接

### Step 6：完善错误处理（1-2 天）

**目标**：处理各种失败情况

**任务**：
- 添加 try-except 包裹所有关键操作
- 失败时在 Issue 评论详细错误信息
- 失败时清理远程分支
- 添加日志输出，方便调试

**验收标准**：
- 各种失败情况都有友好提示
- 没有残留的垃圾分支

### Step 7：添加安全限制（1 天）

**目标**：添加安全约束

**任务**：
- 添加文件类型白名单
- 添加修改行数限制
- 添加语法检查（`python -m py_compile`）
- 添加目录黑名单

**验收标准**：
- 尝试修改不允许的文件时被拒绝
- 语法错误的代码不会提交

### Step 8：本地测试脚本（1 天）

**目标**：创建本地测试环境

**任务**：
- 创建 `.github/scripts/agent_issue_executor_test.py`
- 模拟 GitHub Actions 环境
- 测试各个步骤

**验收标准**：
- 可以在本地完整运行一遍流程
- 不消耗真实的 GitHub Actions 配额

### Step 9：编写文档（1 天）

**目标**：完善项目文档

**任务**：
- 创建 `ZHIPU_AGENT_ISSUE_STAGE2_MVP.md`
- 创建 `ZHIPU_AGENT_ISSUE_STAGE2_TEST.md`
- 更新 `ZHIPU_AGENT_ISSUE.md`（总览文档）
- 添加使用示例

**验收标准**：
- 文档清晰，易懂
- 包含完整的使用说明

### Step 10：真实测试与优化（1-2 天）

**目标**：在真实环境中测试并优化

**任务**：
- 在真实 Issue 中测试
- 根据测试结果优化 prompt
- 根据测试结果优化错误处理
- 收集反馈，迭代改进

**验收标准**：
- 至少在 3 个真实 Issue 中成功执行
- 生成的代码质量可接受

---

## 9. 本阶段与下一阶段文件关系

### 9.1 可以直接复用的文件

**`.github/requirements-agent.txt`**：
- 需要新增 `GitPython>=3.1.40`
- 其他依赖可以直接复用

### 9.2 需要扩展的文件

**`.github/workflows/zhipu-agent-issue.yml`**：
- **不需要修改**：保持第一阶段的触发机制
- 第二阶段创建新的 workflow 文件

**`.github/scripts/agent_issue_handler.py`**：
- **方案 A**：直接导入复用
  ```python
  from agent_issue_handler import get_recent_comments, build_context_prompt
  ```
- **方案 B**：提取共同函数到 `agent_common.py`
  - 优点：避免循环依赖
  - 缺点：增加文件数量

**推荐**：方案 A，直接导入复用

### 9.3 需要新增的文件

**新增文件清单**：

```
.github/
├── workflows/
│   └── zhipu-agent-issue-apply.yml      # 新增
├── scripts/
│   ├── agent_issue_executor.py           # 新增
│   ├── git_operations.py                 # 新增
│   └── agent_issue_executor_test.py      # 新增
├── prompts/
│   └── executor_prompt.md                # 新增
└── config/
    └── executor_config.yaml              # 新增

ZHIPU_AGENT_ISSUE_STAGE2_PLAN.md         # 新增（本文档）
ZHIPU_AGENT_ISSUE_STAGE2_MVP.md          # 新增
ZHIPU_AGENT_ISSUE_STAGE2_TEST.md         # 新增
```

### 9.4 建议拆分，避免单文件过大

**当前 `agent_issue_handler.py`**：约 230 行

**预计 `agent_issue_executor.py`**：约 400-500 行（如果包含所有逻辑）

**建议拆分**：

```
agent_issue_executor.py (主入口，约 150 行)
├── git_operations.py (Git 操作，约 150 行)
├── code_generator.py (代码生成，约 150 行)
└── executor_prompt.md (Prompt 模板，约 100 行)
```

**优点**：
- 每个文件职责单一
- 便于单独测试
- 便于后续扩展

**缺点**：
- 文件数量增加
- 需要管理文件间依赖

**推荐**：MVP 可以先不拆分，等第二阶段稳定后再重构

---

## 10. 最终建议

### 10.1 最推荐的架构方案

**推荐方案**：渐进式架构

**MVP 阶段**（当前）：
```
agent_issue_executor.py (单文件，约 400 行)
├── 主流程逻辑
├── Git 操作（内联函数）
└── AI 调用（内联函数）
```

**后续优化**（第二阶段稳定后）：
```
agent_issue_executor.py (主入口，约 150 行)
├── git_operations.py (独立模块)
├── code_generator.py (独立模块)
└── executor_prompt.md (独立模板)
```

**理由**：
- MVP 先跑通核心流程
- 避免过度设计
- 后续根据实际需求重构

### 10.2 是否建议拆分子阶段

**建议**：不拆分，直接实现 MVP

**理由**：
- 第二阶段的目标明确，范围可控
- 拆分会增加文档和管理工作量
- MVP 已经是"最小可行版本"，天然是子集

**如果必须拆分**，建议：
- **2A**：只实现 Step 1-6（基础功能）
- **2B**：只实现 Step 7（安全限制）
- **2C**：只实现 Step 9-10（文档和优化）

### 10.3 当前仓库最适合从哪一步开始落地

**推荐起点**：**Step 1 + Step 2**

**原因**：
- 这两步风险最低，不涉及代码修改
- 可以快速验证触发机制和权限配置
- 可以复用第一阶段的代码

**执行顺序**：
1. 先完成 Step 1（基础框架）
2. 再完成 Step 2（读取 Issue 和生成计划）
3. 然后一次性完成 Step 3-6（核心功能）
4. 最后完成 Step 7-10（完善和优化）

**关键里程碑**：
- 里程碑 1：Step 2 完成（能生成计划）
- 里程碑 2：Step 6 完成（能创建 PR）
- 里程碑 3：Step 10 完成（可正式使用）

---

## 附录：快速参考

### A. 关键命令

| 命令 | 功能 | 阶段 |
|------|------|------|
| `@zhipu` | 生成执行计划 | 第一阶段 |
| `/zhipu-apply` | 执行代码修改 | 第二阶段 |
| `/zhipu-apply-dry-run` | 预览执行内容 | 第二阶段（可选） |

### B. 关键文件

| 文件 | 职责 | 阶段 |
|------|------|------|
| `zhipu-agent-issue.yml` | 第一阶段 workflow | 第一阶段 |
| `zhipu-agent-issue-apply.yml` | 第二阶段 workflow | 第二阶段 |
| `agent_issue_handler.py` | 计划生成脚本 | 第一阶段 |
| `agent_issue_executor.py` | 代码执行脚本 | 第二阶段 |
| `git_operations.py` | Git 操作封装 | 第二阶段 |

### C. 环境变量

| 变量 | 用途 | 阶段 |
|------|------|------|
| `GITHUB_TOKEN` | GitHub API 访问 | 两个阶段 |
| `ZHIPU_API_KEY` | 智谱 AI 访问 | 两个阶段 |
| `REPO` | 仓库名 | 两个阶段 |
| `ISSUE_NUMBER` | Issue 编号 | 两个阶段 |
| `DRY_RUN` | 是否 dry-run | 第二阶段 |

---

**文档版本**：v1.0
**创建日期**：2026-04-20
**作者**：Claude Code
**状态**：待用户确认
