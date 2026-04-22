# Stage 6 合并前执行顺序

本文档提供 Stage 6 Draft PR 合并前的逐步操作指南。

**适用阶段**：Stage 6 完成后的 MVP 收尾阶段  
**当前限制**：仅支持 `README.md` 单文件修改  
**预计耗时**：15-20 分钟（纯 README.md 修改）

---

## 执行前准备

```bash
# 1. 确认当前分支
git branch
# 应显示 * main

# 2. 同步最新代码
git pull origin main

# 3. 查看最近的 PR
gh pr list --state open --limit 5
```

---

## 执行顺序（共 8 步）

### 步骤 1：打开 Draft PR（2 分钟）

**操作：**
1. 访问 GitHub 仓库 Pull Requests 页面
2. 找到由 `/zhipu-apply` 创建的 Draft PR
3. 打开 PR 页面

**检查：**
- [ ] PR 是 Draft 状态
- [ ] 分支名称格式：`zhipu/issue-{N}`
- [ ] 标题清晰描述修改内容

**如找不到 PR：**
- 检查 Issue 中是否有 Step 6 的回复链接
- 查看 GitHub Actions 运行日志

---

### 步骤 2：回顾原 Issue 需求（3 分钟）

**操作：**
1. 在 PR 页面找到链接到原 Issue
2. 点击进入 Issue 页面
3. 重新阅读 Issue 完整描述

**检查：**
- [ ] 理解 Issue 提出的问题
- [ ] 明确期望的修改目标
- [ ] 确认是否有附加要求

---

### 步骤 3：检查修改文件范围（2 分钟）

**操作：**
1. 在 PR 页面点击 "Files changed" 标签
2. 查看修改的文件列表

**关键检查：**
- [ ] **只能修改 `README.md`**
- [ ] 没有修改 `.py`、`.yml`、`.json` 等代码文件
- [ ] 没有修改多个文件

**如发现修改了其他文件：**
⚠️ **停止 review，按以下步骤操作：**
1. 立即关闭 Draft PR
2. 在原 Issue 中评论：
   ```markdown
   ⚠️ Review 发现问题：PR 修改了非 README.md 文件
   
   修改文件：[列出文件名]
   
   请检查 Stage 1 计划和 Stage 2 执行逻辑。
   ```
3. 检查 `.github/scripts/agent_issue_executor.py` 逻辑

---

### 步骤 4：检查 Commit 信息（1 分钟）

**操作：**
1. 在 PR 页面找到 "Commits" 区域
2. 查看提交历史
3. 点击 commit 查看详细修改

**检查：**
- [ ] Commit 数量：1 个
- [ ] Commit message 清晰
- [ ] 修改 diff 合理

---

### 步骤 5：检查修改内容质量（5 分钟）

**操作：**
1. 在 "Files changed" 标签页查看具体修改
2. 逐行检查 diff
3. 对照 Issue 需求验证

**检查项：**
- [ ] **无错别字**
  - 技术名称正确：Zhipu AI、GLM-4-Flash、FastAPI
  - 专有名词大小写一致

- [ ] **格式正确**
  - Markdown 语法正确
  - 标题层级合理
  - 代码块有语言标识

- [ ] **符合 Issue 需求**
  - Issue 中提到的所有点都已修改
  - 没有遗漏关键修改
  - 没有超出需求范围的额外修改

- [ ] **无破坏性变更**
  - 没有删除重要内容
  - 没有改变原有结构（除非 Issue 明确要求）

---

### 步骤 6：检查 GitHub Actions 状态（2 分钟）

**操作：**
1. 在 PR 页面找到 "Checks" 区域
2. 查看所有 CI/CD 检查项状态

**检查：**
- [ ] 所有检查项为 ✅
- [ ] 没有 ❌ 失败的检查

**如有检查失败：**
1. 点击失败的检查项
2. 查看详细日志
3. 根据原因决定：
   - 临时故障 → 重新运行检查
   - 代码问题 → 修复后重新 push
   - 配置问题 → 修复配置后重新运行

---

### 步骤 7：本地功能测试（按需执行，3-5 分钟）

> **⚠️ 当前 MVP 阶段的 `README.md` 文案修改通常不需要此步骤**  
> **仅在修改涉及 API 配置、环境变量、服务启动等内容时执行**

**判断是否需要执行：**

| 修改类型 | 是否需要本地测试 |
|---------|----------------|
| 纯文案修改、格式调整 | ❌ 不需要 |
| 错别字修复 | ❌ 不需要 |
| 说明性文字补充 | ❌ 不需要 |
| API 配置说明修改 | ✅ 建议执行 |
| 环境变量配置说明修改 | ✅ 建议执行 |
| 服务启动说明修改 | ✅ 建议执行 |

**如不需要本地测试：**
- [ ] 跳过此步骤，直接进入步骤 8

**如需要本地测试：**

```bash
# 1. 切换到 PR 分支
git fetch origin
git checkout zhipu/issue-{N}

# 2. 安装依赖
uv sync

# 3. 启动服务
cd backend
uv run uvicorn app:app --reload --port 8000

# 4. 检查启动日志
# 应看到 "Loaded X courses with Y chunks"

# 5. 测试查询接口
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询", "session_id": null}'

# 6. 切回 main 分支
git checkout main
```

**检查：**
- [ ] 服务启动成功
- [ ] 查询接口返回正常

---

### 步骤 8：合并决策（1 分钟）

### 情况 A：所有检查通过，准备合并

**操作：**
1. 在 Draft PR 页面点击 "Ready for review"
2. 添加最终评论（可选）：
   ```markdown
   ## ✅ Review 通过
   
   所有检查项通过：
   - [x] 只修改 README.md
   - [x] 符合 Issue 需求
   - [x] 无错别字和格式问题
   - [x] GitHub Actions 正常
   
   批准合并。
   ```
3. 点击 "Merge pull request"
4. 选择 "Merge commit"
5. 点击 "Confirm merge"
6. 删除分支 `zhipu/issue-{N}`（可选）

**合并后操作：**
```bash
# 同步本地代码
git pull origin main

# 确认合并成功
git log --oneline -3
```

### 情况 B：发现小问题，需要修改

**操作：**
1. 在 PR 中评论说明问题
2. 人工直接在分支修改并 push：
   ```bash
   git checkout zhipu/issue-{N}
   # ... 修改文件 ...
   git add README.md
   git commit -m "docs: fix review feedback"
   git push origin zhipu/issue-{N}
   ```
3. 重新执行步骤 5-6（步骤 7 按需）

### 情况 C：发现严重问题，需要关闭 PR

**操作：**
1. 在 PR 中评论：
   ```markdown
   ## ⚠️ Review 发现严重问题
   
   [描述问题]
   
   **决定：**
   - 关闭当前 Draft PR
   - 在 Issue 中记录问题
   - 修复系统后重新执行流程
   ```
2. 关闭 PR（不要合并）
3. 在原 Issue 中记录详细问题
4. 检查 `.github/scripts/agent_issue_executor.py` 逻辑
5. 修复后重新测试 Stage 1-6 完整流程

---

## 执行后验证

### 合并成功后验证（2 分钟）

```bash
# 1. 确认本地已同步
git pull origin main

# 2. 查看 git 历史
git log --oneline -5
# 应看到合并的 commit

# 3. 确认分支已删除（远程）
git branch -r
# 不应看到 zhipu/issue-{N}
```

**检查：**
- [ ] 合并 commit 已在 git 历史中
- [ ] PR 分支已删除

---

## 常见问题 FAQ

### Q1: 如果 PR 修改了多个文件怎么办？

**A:** 当前 MVP 限制只能修改 `README.md`。如发现修改了多个文件：
1. ⛔ 不要合并
2. 检查 Stage 1 计划和 Stage 2 执行逻辑
3. 在 Issue 中记录问题
4. 修复后重新测试

### Q2: 如果 GitHub Actions 检查失败怎么办？

**A:** 
1. 查看失败日志
2. 临时故障 → 重新运行
3. 代码问题 → 修复后重新 push
4. 配置问题 → 修复配置后重新运行

### Q3: 如果修改内容与 Issue 需求不符怎么办？

**A:**
1. 重新阅读 Issue，确认理解正确
2. 在 PR 中评论讨论
3. 如需大改 → 关闭 PR，重新执行 `/zhipu-apply`
4. 如可小改 → 人工修改后继续

### Q4: 如果合并后发现严重问题怎么办？

**A:** 立即回滚（优先使用 `git revert`）：

```bash
# 1. 回滚合并（推荐：git revert）
git revert <merge-commit-hash> -m 1

# 2. 推送到 main（正常推送）
git push origin main

# 3. 在 Issue 中说明情况
```

**特殊情况（谨慎使用 `--force-with-lease`）：**
仅在确认需要完全删除该 commit、且没有其他人正在推送时使用。

```bash
# ⚠️ 谨慎使用
git reset --hard <commit-before-merge>
git push origin main --force-with-lease
```

---

## 时间估算

| 步骤 | 预计耗时 | 必须执行 |
|-----|---------|---------|
| 步骤 1：打开 Draft PR | 2 分钟 | ✅ 是 |
| 步骤 2：回顾原 Issue | 3 分钟 | ✅ 是 |
| 步骤 3：检查修改文件范围 | 2 分钟 | ✅ 是 |
| 步骤 4：检查 Commit 信息 | 1 分钟 | ✅ 是 |
| 步骤 5：检查修改内容质量 | 5 分钟 | ✅ 是 |
| 步骤 6：检查 GitHub Actions | 2 分钟 | ✅ 是 |
| 步骤 7：本地功能测试 | 3-5 分钟 | ⚠️ 按需 |
| 步骤 8：合并决策 | 1 分钟 | ✅ 是 |
| **总计（必须）** | **16 分钟** | - |
| **总计（含测试）** | **19-21 分钟** | - |

---

## 快速命令参考

```bash
# 查看 PR 列表
gh pr list --state open

# 查看 PR 详情
gh pr view <pr-number>

# 查看 PR diff
gh pr diff <pr-number>

# 切换分支
git checkout zhipu/issue-{N}

# 同步最新代码
git pull origin main
```

---

## 相关文档

- **PR Review 清单**：`PR_REVIEW_CHECKLIST.md`
- **Zhipu Agent 使用指南**：`ZHIPU_AGENT_USAGE.md`
- **项目总文档**：`README.md`

---

**文档维护**：@yyd841122  
**最后更新**：2026-04-22
