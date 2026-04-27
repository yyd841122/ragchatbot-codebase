# Zhipu AI Agent 使用文档

本文档说明如何在当前仓库中使用 Zhipu AI Agent，从 GitHub Issue 生成执行计划、自动修改目标文件（Markdown 文件或配置文件），并创建 Draft Pull Request。

---

## 当前已支持能力

当前仓库已经验证通过的能力如下：

1. **Stage 1：计划生成**
   - 在 Issue 中评论 `@zhipu`
   - Agent 会生成结构化执行计划

2. **Stage 2：执行链路**
   - 在 Issue 中评论 `/zhipu-apply`
   - 系统会自动执行以下步骤：
     - Step 1：识别触发命令
     - Step 2：读取 Issue 上下文和 Stage 1 计划
     - Step 3：创建工作分支 `zhipu/issue-{issue_number}`
     - Step 4：预览第一个目标文件
     - Step 5：修改目标文件并创建 commit
       - 对于 Markdown 文件：AI 生成完整文件内容
       - 对于配置文件（.gitignore、.env.example）：AI 生成追加内容，程序追加到文件末尾
     - Step 6：自动创建 Draft PR

3. **人工确认**
   - Draft PR 不会自动 merge
   - 仍需要人工 review 后再决定是否合并

---

## 推荐使用流程

### 第一步：创建 Issue

在仓库中创建一个新 Issue，明确说明修改目标。

### 第二步：生成结构化计划

在 Issue 中评论：

```text
@zhipu
```

Agent 会生成结构化计划，包括问题理解、计划修改文件、Todo List、风险提示等内容。

### 第三步：检查计划

重点检查 `### 计划修改文件` 章节，确保第一个文件是仓库中真实存在的文件，且符合当前支持范围。

**支持的文件类型**：
- Markdown 文件（.md）：根目录或一级子目录
- 配置文件：仅 `.gitignore` 和 `.env.example`（根目录，append-only 模式）

推荐写法：

**Markdown 文件**：
```markdown
### 计划修改文件
- `README.md` - [更新说明]
```

**配置文件**：
```markdown
### 计划修改文件
- `.gitignore` - 追加忽略规则
- `.env.example` - 追加环境变量示例
```

### 第四步：执行自动化流程

在执行 `/zhipu-apply` 之前，请先确认 `### 计划修改文件` 的第一个文件是仓库中真实存在的文件，且符合当前支持范围。

确认计划无误后，在同一个 Issue 中评论：

```text
/zhipu-apply
```

系统会继续执行 Step 3 ~ Step 6，并尝试自动创建 Draft PR。

### 第五步：人工 Review Draft PR

如果 Step 6 成功，系统会在 Issue 中回帖，并附上 Draft PR 链接。

然后由人工打开该 PR 进行 review。

---

## Issue 编写要求

为了提高成功率，建议遵循以下规则：

### 核心要求

**`### 计划修改文件`章节的第一个文件必须是仓库中真实存在的文件**

**支持的文件类型**：
- Markdown 文件（.md）：根目录或一级子目录
- 配置文件：仅 `.gitignore` 和 `.env.example`（根目录，append-only 模式）

### 推荐格式

**Markdown 文件**：
```markdown
### 计划修改文件
- `README.md` - [更新说明]
```

**配置文件**：
```markdown
### 计划修改文件
- `.gitignore` - 追加忽略规则
- `.env.example` - 追加环境变量示例
```

### 不建议的写法

- ❌ 不要使用占位路径：`path/to/README.md`
- ❌ 当前不要把 `.py`、`.yml`、`.txt` 等文件放在第一个文件位置
- ❌ 配置文件不要放在子目录（如 `config/.gitignore`）

---

## 人工 Review 怎么做

人工 review 在线上 GitHub PR 页面完成，不是在本地完成。

操作步骤如下：

1. 打开 Issue 中 Step 6 回帖给出的 Draft PR 链接
2. 在 PR 页面查看：
   - `Conversation`
   - `Commits`
   - `Files changed`
3. 重点检查：
   - 修改内容是否符合原始 Issue 目标
   - 是否只改了预期文件
   - 文案是否准确
   - 是否有明显误改、漏改
4. 确认没问题后，点击 **"Ready for review"**
5. 再根据需要执行后续 review / merge

---

## 当前限制

当前版本属于 MVP，限制如下：

- **Markdown 文件**：支持根目录和一级子目录的 `.md` 文件
- **配置文件**：仅支持根目录的 `.gitignore` 和 `.env.example`（append-only 模式）
- **当前只处理第一个目标文件**，不支持多文件批量修改
- **不能使用占位路径**，否则 Step 4 可能读取失败，Step 5 也无法正确执行
- **不会自动 merge**，只会创建 Draft PR，必须人工 review 后再决定是否合并
- **配置文件只能追加**，不能修改或删除现有内容
- **仓库需预先完成 GitHub Actions 与 PR 创建权限配置**，否则 Step 6 可能失败

---

## 常见失败原因

### 1. Step 4 文件读取失败
- **常见原因**：Stage 1 计划里的第一个文件不是仓库真实存在的文件，或写成了占位路径，或文件名被错误拼接
- **解决方法**：确保第一个文件是真实存在的 `README.md`

### 2. Step 5 跳过非支持文件
- **常见原因**：第一个目标文件不在当前支持范围内（如代码文件、深层目录文件）
- **解决方法**：确保第一个文件符合当前支持范围
  - Markdown 文件：根目录或一级子目录的 `.md` 文件
  - 配置文件：仅根目录的 `.gitignore`、`.env.example`（append-only 模式）

### 3. Step 6 创建 Draft PR 失败
- **常见原因**：仓库未完成 GitHub Actions / PR 权限配置，或当前分支没有实际新增 commit
- **解决方法**：联系仓库管理员确认权限配置，确保 Issue 中的修改需求会导致实际内容变化

### 4. 没有成功触发执行
- **常见原因**：没有评论 `@zhipu` 或 `/zhipu-apply`，或触发者不具备对应仓库权限
- **解决方法**：确保评论中包含触发命令，且触发者有 OWNER/COLLABORATOR/MEMBER 权限

---

## 总结

当前这套流程已经可以稳定完成以下闭环：

**Issue → 结构化计划 → 工作分支 → 文件修改（Markdown 或配置文件）→ commit → Draft PR**

**当前支持范围**：
- Markdown 文件：根目录和一级子目录的 `.md` 文件
- 配置文件：仅根目录的 `.gitignore`、`.env.example`（append-only 模式）

现阶段最适合用于：
- Markdown 文档更新
- 配置文件 append-only 追加
- 小范围、可人工复核的改动

不建议当前直接用于：
- 多文件修改
- 代码文件修改
- 复杂重构任务
