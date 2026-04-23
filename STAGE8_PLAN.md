**文件名**：`STAGE8_PLAN.md`
**计划版本**：v1.0
**制定日期**：2026-04-23
**适用范围**：Stage 8 v1 - Markdown 文档扩展

---

## 1. 当前能力边界

**当前系统（Stage 1-7）已验证的能力**：
- ✅ Issue 评论触发（`@zhipu`、`/zhipu-apply`）
- ✅ AI 生成结构化执行计划
- ✅ 自动创建工作分支（`zhipu/issue-{n}`）
- ✅ 自动修改**根目录 `README.md`** 并创建 commit
- ✅ 自动创建 Draft PR
- ✅ 人工 review 后合并

**当前硬编码的限制**（在 `agent_issue_executor.py:1476`）：
```python
if basename != "readme.md":
    # 跳过处理，回复不支持消息
```

**当前不支持的文件**：
- ❌ 其他 `.md` 文档（如 `CHANGELOG.md`、`docs/GUIDE.md`）
- ❌ 配置文件（`.env.example`、`.gitignore`、`requirements.txt` 等）
- ❌ 代码文件（`.py`、`.js`、`.yml` 等）

---

## 2. Stage 8 v1 核心目标

**主目标**：
从"仅支持根目录 `README.md`"扩展到"支持安全的 Markdown 文档文件修改"。

**具体范围**：
- ✅ 根目录的常见 `.md` 文件（如 `CHANGELOG.md`、`CONTRIBUTING.md`）
- ✅ 一级子目录中的 `.md` 文件（如 `docs/GUIDE.md`、`docs/FAQ.md`）
- ❌ 不支持更深层的目录（如 `docs/deep/file.md`）
- ❌ 不支持其他文件类型

**非目标（Stage 8 v1 不做的事情）**：
- ❌ 不支持配置文件（`.env.example`、`.gitignore`、`requirements.txt`）
- ❌ 不支持代码文件（`.py`、`.js`、`.yml` 等）
- ❌ 不支持多文件批量修改
- ❌ 不支持删除/重命名/创建文件
- ❌ 不改整体架构，只在现有框架上扩展

**后续候选扩展（Stage 9+ 评估）**：
- `.env.example`、`.gitignore`（仅追加）、`requirements.txt`（仅追加）
- 简单的 YAML/JSON 配置文件
- 更深层的目录结构

---

## 3. 支持的文件类型与路径范围

### 3.1 文件类型

**仅支持 `.md` 文件**，具体包括但不限于：

| 文件路径示例 | 说明 |
|-------------|------|
| `README.md` | 根目录 README（已支持） |
| `CHANGELOG.md` | 变更日志 |
| `CONTRIBUTING.md` | 贡献指南 |
| `docs/GUIDE.md` | 一级子目录文档 |
| `docs/FAQ.md` | 一级子目录常见问题 |
| `docs/ARCHITECTURE.md` | 一级子目录架构说明 |

### 3.2 路径安全规则

**允许的路径**：
- ✅ 根目录：`README.md`、`CHANGELOG.md`、`CONTRIBUTING.md`
- ✅ 一级子目录：`docs/*.md`、`guides/*.md`

**禁止的路径**：
- ❌ 相对路径跳转：`../../etc.md`、`../secret.md`
- ❌ 更深层目录：`docs/deep/file.md`、`docs/a/b/c.md`
- ❌ 绝对路径：`/etc/file.md`

**实现口径**：
- 路径按 `/` 分隔后最多 2 段
- 例如：`README.md`（1 段）、`docs/GUIDE.md`（2 段）允许
- 例如：`docs/deep/file.md`（3 段）不允许

**实现方式**：
```python
def is_safe_path(file_path: str) -> bool:
    """检查路径是否安全

    规则：
    - 禁止 '../' 跳转
    - 路径按 '/' 分隔后最多 2 段
    """
    # 禁止相对路径跳转
    if '../' in file_path:
        return False

    # 统一路径分隔符
    normalized = file_path.replace('\\', '/')

    # 检查深度（按 / 分隔后最多 2 段）
    parts = normalized.split('/')
    return len(parts) <= 2
```

---

## 4. 最小可行实施顺序

### 阶段 8.1：扩展 Markdown 文档支持（预计 1-2 周）

#### 步骤 1：修改文件类型检查逻辑

**目标**：从"仅支持 README.md"改为"支持 .md 文件"

**需要修改的代码文件**：
- `.github/scripts/agent_issue_executor.py`

**具体改动**：
```python
# 旧代码（line 1476）
if basename != "readme.md":
    print(f"  ℹ️ 文件 {basename} 不在支持范围内（仅支持 README.md）")
    reply_message = build_step5_unsupported_file_message(file_path)
    # ...

# 新代码
def is_supported_markdown_file(file_path: str) -> bool:
    """检查是否为支持的 Markdown 文件"""
    # 必须以 .md 结尾
    if not file_path.lower().endswith('.md'):
        return False

    # 路径安全检查
    if not is_safe_path(file_path):
        return False

    return True

# 在 Step 5 中使用
if not is_supported_markdown_file(file_path):
    print(f"  ℹ️ 文件 {file_path} 不在支持范围内（仅支持根目录和一级子目录的 .md 文件）")
    reply_message = build_step5_unsupported_file_message(file_path)
    # ...
```

---

#### 步骤 2：改进 Stage 1 的 AI Prompt

**目标**：引导 AI 生成更准确的 `.md` 文件路径

**需要修改的代码文件**：
- `.github/scripts/agent_issue_handler.py`

**具体改动**：
修改 Stage 1 的 prompt 构建函数（`build_context_prompt`），添加文件类型引导：

```python
# 在 build_context_prompt 函数中的 system_prompt 添加：
system_prompt += """

### 支持的文件类型
当前仅支持 Markdown 文档文件（.md）：

**允许的路径示例**：
- `README.md` - 根目录 README
- `CHANGELOG.md` - 变更日志
- `CONTRIBUTING.md` - 贡献指南
- `docs/GUIDE.md` - 一级子目录文档
- `docs/FAQ.md` - 一级子目录常见问题

**禁止的路径**：
- 相对路径跳转：`../file.md`
- 更深层目录：`docs/deep/file.md`（路径超过 2 段）
- 非 Markdown 文件：`config.py`, `.env.example`

### 计划修改文件格式要求
在"计划修改文件"章节中，请遵循以下格式：
- `README.md` - [修改目的]
- `CHANGELOG.md` - [修改目的]
- `docs/GUIDE.md` - [修改目的]

重要：确保文件路径真实存在，且符合上述路径规则。
"""
```

---

#### 步骤 3：添加路径存在性验证

**目标**：在 Step 5 执行前，先验证文件是否存在

**需要修改的代码文件**：
- `.github/scripts/agent_issue_executor.py`

**具体改动**：
```python
def verify_file_exists(repo, file_path: str) -> bool:
    """验证文件是否存在

    Args:
        repo: Github 仓库对象
        file_path: 文件路径

    Returns:
        文件是否存在
    """
    try:
        repo.get_contents(file_path)
        return True
    except UnknownObjectException:
        return False

# 在 execute_step5 中调用
def execute_step5(repo, issue, plan_content, branch_name):
    # ...

    # 验证文件是否存在
    print("🔍 验证文件是否存在...")
    if not verify_file_exists(repo, file_path):
        print(f"  ❌ 文件 {file_path} 不存在")
        reply_message = build_step5_file_not_found_message(file_path)
        issue.create_comment(reply_message)
        return {'status': 'failed', 'reason': f'文件 {file_path} 不存在'}

    print(f"  ✅ 文件 {file_path} 存在")
```

---

#### 步骤 4：更新错误提示消息

**目标**：提供更清晰的错误提示和修复建议

**需要修改的代码文件**：
- `.github/scripts/agent_issue_executor.py`

**具体改动**：
```python
def build_step5_unsupported_file_message(file_path: str) -> str:
    """构建不支持的文件类型的回复消息"""
    return f"""## 🤖 Zhipu Stage 2 - Step 5 执行结果

**状态**: ❌ 跳过文件修改

**原因**: 文件 `{file_path}` 不在支持范围内

**当前支持的文件类型**：
- ✅ 根目录的 `.md` 文件（如 `README.md`、`CHANGELOG.md`）
- ✅ 一级子目录的 `.md` 文件（如 `docs/GUIDE.md`）
- ❌ 不支持更深层的目录（如 `docs/deep/file.md`）
- ❌ 不支持其他文件类型（如 `.py`、`.env.example`、`.gitignore`）

**如何修复**：
1. 检查文件路径是否符合上述规则
2. 在 Issue 中重新评论 `@zhipu`，生成修正后的计划
3. 确保 `### 计划修改文件` 章节中的第一个文件符合规则

---

🤖 由 Zhipu AI Stage 2 - Step 5 生成
"""
```

---

#### 步骤 5：测试验证

**测试矩阵**：

| 测试用例 | 文件路径 | 预期结果 | 验证方法 |
|---------|---------|---------|---------|
| 正常样本 1 | `CHANGELOG.md` | ✅ 成功修改 | 检查 Draft PR diff |
| 正常样本 2 | `docs/GUIDE.md` | ✅ 成功修改 | 检查 Draft PR diff |
| 异常路径 1 | `../secret.md` | ❌ 拒绝（路径跳转） | 检查是否报错 |
| 异常路径 2 | `docs/deep/file.md` | ❌ 拒绝（层级过深） | 检查是否报错 |
| 异常类型 1 | `config.py` | ❌ 拒绝（非 .md） | 检查是否报错 |
| 异常存在性 | `nonexist.md` | ❌ 拒绝（文件不存在） | 检查是否报错 |

**验收标准**：
- 正常样本测试应稳定通过
- 异常路径应能明确拦截并给出清晰的错误提示
- Draft PR 的 diff 应保持可理解、可追踪、可回滚

---

## 5. 风险控制与人工 Review 策略

### 5.1 技术风险控制

**1. 文件类型白名单**
- 仅允许 `.md` 文件
- 其他类型直接拒绝

**2. 路径安全检查**（见上文 3.2）
- 禁止相对路径跳转
- 限制路径深度（按 `/` 分隔后最多 2 段）

**3. 文件存在性验证**（见上文步骤 3）
- 调用 GitHub API 验证文件是否存在
- 避免尝试修改不存在的文件

**4. 内容长度限制**
- 单次修改不超过 500 行
- 单行不超过 1000 字符

---

### 5.2 人工 Review 流程

**当前流程（保持不变）**：
```
Issue → AI 计划 → /zhipu-apply → Draft PR → 人工 Review → 合并
```

**Draft PR Review 关注点**：
1. 文件类型是否为 `.md`？
2. 路径是否安全（无 `../`，无深层目录）？
3. 修改内容是否符合 Issue 需求？
4. Markdown 格式是否正确？
5. 是否有明显的错误或不合理内容？

**失败时的标准处理流程**：
```markdown
### 修复失败的标准流程

1. 检查 GitHub Actions 日志，找到失败步骤
2. 查看 Issue 中的 AI 错误提示
3. 关闭失败的 Draft PR（可选）
4. 重新评论 `@zhipu`，生成修正后的计划
5. 再次执行 `/zhipu-apply`
```

---

## 6. 需要更新的文档

### 6.1 必须更新的文档

**1. `ZHIPU_GUIDE.md`**
- 更新"当前支持能力"章节
- 添加"支持的文件类型"章节

**2. `ZHIPU_AGENT_USAGE.md`**
- 更新"当前已支持能力"章节
- 更新"Issue 编写要求"（移除"必须是 README.md"的限制）
- 更新"推荐写法"示例

**3. `PR_REVIEW_CHECKLIST.md`**
- 添加 Stage 8 新增检查项：
  ```markdown
  ### Stage 8 新增检查项（Markdown 文档支持）

  - [ ] 文件类型是否为 .md？
  - [ ] 路径是否安全？（无 ../，无深层目录）
  - [ ] 修改内容是否符合 Issue 需求？
  - [ ] Markdown 格式是否正确？
  ```

**4. `STAGE8_COMPLETE.md`（新增）**
- 记录 Stage 8 v1 的实现细节
- 记录测试结果和已知问题

---

### 6.2 可选更新的文档

**1. `README.md`**
- 更新 Zhipu Agent 功能说明（如果有）

**2. `AUTOMATION_README.md`**
- 后续更新，非优先

---

## 7. 预计需要修改的代码文件

### 7.1 核心修改

**1. `.github/scripts/agent_issue_executor.py`**
- 添加 `is_supported_markdown_file()` 函数
- 添加 `is_safe_path()` 函数
- 添加 `verify_file_exists()` 函数
- 修改 `execute_step5()` 中的文件类型检查逻辑
- 更新 `build_step5_unsupported_file_message()` 的错误提示

**预计改动行数**：+80 行（新增函数和逻辑）

---

### 7.2 Prompt 改进

**2. `.github/scripts/agent_issue_handler.py`**
- 修改 Stage 1 的 prompt 构建函数（`build_context_prompt`）
- 添加文件类型引导章节

**预计改动行数**：+15 行（prompt 内容）

---

### 7.3 测试脚本（可选）

**3. `.github/scripts/test_file_validation.py`（新增）**
- 单元测试：`test_safe_path_check()`
- 单元测试：`test_is_supported_markdown_file()`
- 集成测试：模拟不同文件路径的处理

**预计行数**：+100 行（可选）

---

## 8. 验证与测试建议

### 8.1 单元测试（可选）

```python
# test_file_validation.py

def test_safe_path_check():
    """测试路径安全检查"""
    assert is_safe_path("README.md") == True
    assert is_safe_path("CHANGELOG.md") == True
    assert is_safe_path("docs/GUIDE.md") == True
    assert is_safe_path("../etc.md") == False
    assert is_safe_path("docs/deep/file.md") == False
    assert is_safe_path("../../secret.md") == False

def test_is_supported_markdown_file():
    """测试文件类型检查"""
    assert is_supported_markdown_file("README.md") == True
    assert is_supported_markdown_file("CHANGELOG.md") == True
    assert is_supported_markdown_file("docs/GUIDE.md") == True
    assert is_supported_markdown_file("config.py") == False
    assert is_supported_markdown_file(".env.example") == False
    assert is_supported_markdown_file("docs/deep/file.md") == False
```

---

### 8.2 真实场景测试

**测试 Issue 模板**：
```markdown
## 测试：修改 CHANGELOG.md

### 任务描述
请在 CHANGELOG.md 中追加一个新的版本记录。

### 具体要求
- 版本号：1.0.0
- 日期：2026-04-23
- 变更内容：添加 Markdown 文档扩展支持

### 预期结果
- 成功修改 CHANGELOG.md
- 生成清晰的 Draft PR diff
```

---

### 8.3 灰度发布策略（已确认）

**方案 A（已选择）：测试分支验证**
1. 创建测试分支 `test/zhipu-stage8`
2. 在测试分支中修改代码
3. 推送到 GitHub，触发 Actions
4. 创建测试 Issue，完成若干真实样本验证
5. 收集反馈，修复问题
6. 验证通过后合并到 main

---

## 9. 用户确认的决策

基于 Stage 8 v1 草案讨论，用户已确认以下决策：

### 决策 1：Stage 8 v1 的范围 ✅
**已选择**：方案 A - 仅支持 Markdown 文档文件（`.md`）

---

### 决策 2：路径深度限制 ✅
**已选择**：方案 B - 允许根目录 + 一级子目录（如 `docs/*.md`）

**实现口径**：
- 路径按 `/` 分隔后最多 2 段
- 例如：`README.md`（1 段）、`docs/GUIDE.md`（2 段）允许
- 例如：`docs/deep/file.md`（3 段）不允许

---

### 决策 3：灰度发布策略 ✅
**已选择**：方案 A - 先走测试分支验证

**流程**：
1. 创建测试分支 `test/zhipu-stage8`
2. 完成若干真实样本验证
3. 验证通过后合并到 main

---

## 10. 预计时间线

**阶段 8.1：扩展 Markdown 文档支持**
- 步骤 1-2：修改代码和 prompt（2-3 天）
- 步骤 3-4：添加验证和错误提示（1-2 天）
- 步骤 5：测试验证（2-3 天）
- 文档更新（1 天）
- **总计：6-9 天**

---

## 11. 相关文档

- **Stage 7 完成总结**：`STAGE7_COMPLETE.md`
- **Stage 7 原始计划**：`STAGE7_PLAN.md`
- **使用指南**：`ZHIPU_AGENT_USAGE.md`
- **文档导航**：`ZHIPU_GUIDE.md`
- **PR Review 清单**：`PR_REVIEW_CHECKLIST.md`

---

**文档维护**：@yyd841122
**最后更新**：2026-04-23

---

## 下一步

**基于用户确认的决策，准备开始实施阶段 8.1**：
1. 创建测试分支 `test/zhipu-stage8`
2. 按步骤 1-5 依次实施
3. 完成真实样本验证
4. 验证通过后合并到 main
