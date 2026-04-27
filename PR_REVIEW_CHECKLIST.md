# PR Review Checklist - Stage 8.5 边界测试补充

本文档用于 Stage 8.5 Draft PR 的人工 review 检查。

**适用阶段**：Stage 8.5 完成后的边界测试补充阶段
**当前支持范围**：Markdown 文件（根目录和一级子目录）+ 配置文件（仅根目录 .gitignore、.env.example）
**文档版本**：v3.1
**更新日期**：2026-04-27

---

## 快速检查清单（必做项）

### 1. Draft PR 基础验证

- [ ] **PR 触发来源**
  - 由 `/zhipu-apply` 触发 Stage 2 自动创建
  - PR 状态为 Draft（非 "Ready for review"）
  - 分支名称格式：`zhipu/issue-{issue_number}`

- [ ] **Commit 信息**
  - Commit 数量：1 个
  - Commit message 清晰

- [ ] **修改文件范围（关键）**
  - **当前支持范围**：
    - Markdown 文件：根目录和一级子目录的 `.md` 文件
    - 配置文件：根目录的 `.gitignore`、`.env.example`（append-only 模式）
  - 在 PR 页面 "Files changed" 标签确认
  - 如发现代码文件或深层目录文件 → 立即停止 review，按第 4 节"严重问题"处理

### 2. 修改内容质量检查

- [ ] **文案准确性**
  - 无错别字
  - 技术名称正确（Zhipu AI、GLM-4-Flash、FastAPI）
  - 专有名词大小写一致

- [ ] **格式正确性**
  - Markdown 语法正确
  - 标题层级合理
  - 代码块有语言标识

- [ ] **符合 Issue 需求**
  - 打开源 Issue，重新阅读需求
  - 确认修改解决了提出的问题
  - 没有超出需求范围的额外修改

### 3. GitHub Actions 状态

- [ ] **CI/CD 检查**
  - 在 PR 页面 "Checks" 区域查看
  - 所有检查项为 ✅
  - 如有 ❌ 失败 → 点击日志分析原因

### 4. MVP 限制确认

当前版本 MVP 的限制（必须遵守）：

- [ ] **Markdown 文件**：支持根目录和一级子目录的 `.md` 文件
- [ ] **配置文件**：仅支持根目录的 `.gitignore`、`.env.example`（append-only 模式）
- [ ] **不支持多文件批量修改**
- [ ] **不支持代码文件修改**（`.py`、`.yml` 等）
- [ ] **配置文件只能追加**，不能修改或删除现有内容
- [ ] **必须人工 review 后才能合并**

---

## 按需检查项（当前 README.md 修改通常不需要）

> **说明**：以下检查项仅在修改涉及 API 配置、环境变量、服务启动等内容时需要执行。  
> 纯文案修改可跳过。

### A. 技术影响评估（按需执行）

**适用场景：**
- 修改涉及 API 配置说明
- 修改涉及环境变量配置
- 修改涉及服务启动说明
- 修改涉及 GitHub Actions 配置

**不适用场景（当前常见情况）：**
- 纯文案优化
- 格式调整
- 错别字修复
- 说明性文字补充

**风险等级判断：**

| 风险等级 | 特征 | 处理方式 |
|---------|------|---------|
| 低 | 纯文案修改 | 完成第 2 节检查后可直接合并 |
| 中 | 涉及配置说明 | 建议执行本地测试（B 节） |
| 高 | 涉及代码逻辑 | 🚫 当前 MVP 不应出现 |

### B. 本地功能测试（按需执行）

**适用场景：** 同 A 节"中风险"修改

```bash
# 1. 切换到 PR 分支
git fetch origin
git checkout zhipu/issue-{N}

# 2. 安装依赖并启动服务
uv sync
cd backend
uv run uvicorn app:app --reload --port 8000

# 3. 检查启动日志
# 应看到 "Loaded X courses with Y chunks"

# 4. 测试查询接口（如涉及 API 修改）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询", "session_id": null}'

# 5. 切回 main 分支
git checkout main
```

**检查项：**
- [ ] 服务启动成功
- [ ] 启动日志正常
- [ ] 查询接口返回正常（如适用）

---

## 合并决策

### 通过标准（必须全部满足）

- [ ] ✅ PR 来源正确（`/zhipu-apply` 触发）
- [ ] ✅ 只修改符合支持范围的文件
  - Markdown 文件：根目录和一级子目录的 `.md` 文件
  - 配置文件：根目录的 `.gitignore`、`.env.example`（append-only 模式）
- [ ] ✅ 修改内容符合 Issue 需求
- [ ] ✅ 无错别字、语法错误
- [ ] ✅ GitHub Actions 无失败
- [ ] ✅ 符合 MVP 限制

### 不通过标准（发现任一情况）

- ❌ 修改了不符合支持范围的文件（如代码文件、深层目录文件）
- ❌ 修改内容与 Issue 需求不符
- ❌ 存在错别字或语法错误
- ❌ GitHub Actions 失败

### 合并操作

**如所有检查通过：**

1. 在 Draft PR 页面点击 "Ready for review"
2. 点击 "Merge pull request"
3. 选择 "Merge commit"
4. 点击 "Confirm merge"

**如发现问题：**
参考下一节"问题处理流程"

---

## 问题处理流程

### 小问题（错别字、格式）

**在 PR 中评论：**

```markdown
## Review 反馈

发现以下小问题：
- [ ] 第 X 行："xxx" 应改为 "xxx"
- [ ] 第 Y 行：建议补充说明 "xxx"

请修改后我再次 review。
```

**后续操作：**
- 人工直接在分支修改并 push
- 修改完成后再次 review

### 中等问题（内容不准确、有歧义）

**在 PR 中评论讨论：**

```markdown
## Review 反馈

发现以下问题需要讨论：

1. **问题描述**
   - 当前修改做了 "xxx"
   - 但原 Issue 需求是 "xxx"
   - 是否存在理解偏差？

2. **建议方案**
   - 方案 A：xxx
   - 方案 B：xxx

请确认后再继续。
```

**后续操作：**
- 如需大改 → 关闭当前 PR，在 Issue 中重新执行 `/zhipu-apply`
- 如可小改 → 人工修改后继续

### 严重问题（误改其他文件、核心错误）

**立即关闭 PR：**

```markdown
## ⚠️ Review 发现严重问题

发现以下严重问题：
- [ ] 误改了非 README.md 文件
- [ ] 修改内容与原需求完全不符

**处理决定：**
1. 关闭当前 Draft PR
2. 在 Issue 中记录问题
3. 检查 `.github/scripts/agent_issue_executor.py` 逻辑
4. 修复后重新测试
```

**后续操作：**
- 立即关闭 PR（不要合并）
- 在原 Issue 中详细记录问题
- 检查 Stage 2 执行脚本逻辑
- 本地测试修复后再重新使用

---

## 紧急回滚（特殊情况）

> **⚠️ 仅在已合并 PR 后发现严重问题时使用**

### 推荐方式：git revert（安全）

```bash
# 1. 回滚合并 commit
git revert <merge-commit-hash> -m 1

# 2. 推送到 main（正常推送）
git push origin main

# 3. 在 Issue 中说明情况
```

**优先使用 `git revert` 的原因：**
- 创建新 commit 来撤销修改，保留完整历史
- 不改写 git 历史，安全可逆
- 不影响其他开发者的工作

### 特殊情况：git reset --force（谨慎使用）

> **仅在以下所有条件同时满足时才考虑：**
- 确认需要完全删除该 commit 而非 revert
- 确认没有其他人正在推送或基于该 commit 开发
- 已通知所有团队成员暂停推送
- 已评估风险并做好准备

```bash
# ⚠️ 谨慎使用
git reset --hard <commit-before-merge>
git push origin main --force-with-lease
```

**`--force-with-lease` 仍有风险，仅在必要时使用**

---

## 快速命令参考

```bash
# 查看 PR 详情
gh pr view <pr-number>

# 查看 PR 修改的文件
gh pr diff <pr-number>

# 切换到 PR 分支
git checkout zhipu/issue-{N}

# 同步最新代码
git pull origin main

# 本地测试（按需执行）
uv sync
cd backend
uv run uvicorn app:app --reload --port 8000
```

---

## Stage 8 新增检查项（Markdown 文档支持）

### 文件类型验证

- [ ] **文件类型检查**
  - 修改的文件是否为 `.md` 文件？
  - 文件路径是否在根目录或一级子目录？
  - 路径按 `/` 分隔后是否不超过 2 段？

- [ ] **路径安全检查**
  - 无相对路径跳转（如 `../file.md`）
  - 无绝对路径（如 `/etc/file.md`）
  - 无深层目录（如 `docs/deep/file.md`）

### 修改内容验证

- [ ] **内容符合需求**
  - 修改内容是否符合 Issue 需求？
  - Markdown 格式是否正确？
  - 无明显的错误或不合理内容？

---

## Stage 8.2 新增检查项（配置文件 append-only 支持）

### 配置文件验证

- [ ] **文件类型检查**
  - 修改的文件是否为 `.gitignore` 或 `.env.example`？
  - 文件是否在根目录（路径段数 = 1）？

- [ ] **操作模式验证**
  - 是否为 append-only 模式（只追加，不修改）？
  - Draft PR diff 是否只显示新增内容？
  - 没有修改或删除现有内容？

### 追加内容验证

- [ ] **追加内容格式**
  - `.gitignore`：每行一个忽略规则？
  - `.env.example`：每行一个环境变量示例或注释？
  - 无敏感信息（真实密钥、密码等）？

- [ ] **追加内容质量**
  - 追加的内容是否符合 Issue 需求？
  - 无重复的条目？
  - 无格式错误？

### 安全检查

- [ ] **敏感信息检查**
  - 无真实的 API 密钥
  - 无密码或敏感令牌
  - 无 "your-key-here" 等无意义占位符

---

## Stage 8.4 新增检查项（敏感内容前置识别）

### Stage 1 敏感内容检测验证

- [ ] **Stage 1 计划是否包含敏感内容检测**
  - 如果 Issue 请求追加配置文件内容，检查 Stage 1 计划是否执行了安全检测
  - 检查 Issue 中是否有 Stage 1 拒绝记录（疑似真实密钥）

- [ ] **敏感内容检测是否正确触发**
  - 真实密钥前缀（sk-、ghp_、github_pat_、AIza）是否被正确拒绝
  - 安全占位符（your_api_key_here、example_value）是否被正确允许

---

## Stage 8.5 新增检查项（边界测试补充）

### 边界测试覆盖验证

- [ ] **边界测试是否通过**
  - `.gitignore` 100 行边界、1000 字符边界是否正常
  - `.env.example` 变量名格式验证是否正常（空格、空变量名、非法字符）
  - Stage 1 敏感内容检测边界是否正常（多前缀组合、前缀优先级）

- [ ] **测试覆盖率是否充足**
  - 39 个测试用例是否全部通过
  - 边界场景是否充分覆盖

---

## 相关文档

- **Zhipu Agent 使用指南**：`ZHIPU_AGENT_USAGE.md`
- **Stage 6 合并执行指南**：`STAGE6_MERGE_CHECKLIST.md`
- **项目总文档**：`README.md`

---

**文档维护**：@yyd841122
**最后更新**：2026-04-27
