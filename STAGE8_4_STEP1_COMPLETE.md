# Stage 8.4 Step 1 完成记录

本文档记录 Stage 8.4 Step 1 阶段 1 敏感内容前置识别的完成情况。

**完成日期**：2026-04-27
**版本**：v1.0
**前置阶段**：Stage 8.3（Stage 1 Prompt 增强）
**相关 Issue**：#47, #48, #49, #50

---

## 1. 阶段目标

在 Stage 1 计划生成阶段增加敏感内容前置识别能力，提前拒绝包含疑似真实密钥的 append-only 追加内容，减少无效 Stage 1 计划的生成。

**具体目标**：
- 在 Stage 1 验证流程中检测追加内容安全性
- 拒绝常见密钥前缀（`sk-`、`ghp_`、`github_pat_`、`AIza`）
- 允许安全占位符（`your-zhipu-api-key-here`、`example_value` 等）
- 保持 Stage 5 的完整安全校验作为最终安全网

---

## 2. 已完成能力

### 2.1 核心功能

**新增函数 1：`extract_plan_append_content()`**
- 位置：`.github/scripts/agent_issue_handler.py`（第 69-108 行）
- 功能：从 Stage 1 plan 的 `### 计划追加内容` 章节中提取 fenced code block 内容
- 返回：纯文本追加内容（去除代码块标记）

**新增函数 2：`validate_plan_append_content_safety()`**
- 位置：`.github/scripts/agent_issue_handler.py`（第 111-167 行）
- 功能：对 append-only 追加内容做轻量安全检查
- 检测范围：只检测 append-only 类型任务，跳过其他类型
- 危险前缀：
  - `sk-` - OpenAI API key
  - `ghp_` - GitHub personal access token
  - `github_pat_` - GitHub personal access token (fine-grained)
  - `AIza` - Google API key
- 安全占位符：`your-api-key-here`、`your-zhipu-api-key-here`、`your_openai_api_key`、`your_token_here`、`example_value`、`replace_with_your_key`、`xxx`、`yyy`、`zzz`
- 返回：`(bool, str)` 元组，表示是否通过及错误提示

**集成位置：Stage 1 验证流程**
- 位置：`.github/scripts/agent_issue_handler.py` - `main()` 函数（第 573-582 行）
- 时机：在 `validate_first_file_exists()` 之后，在 `issue.create_comment()` 之前
- 逻辑：
  ```python
  is_safe, safety_error = validate_plan_append_content_safety(ai_response)
  if not is_safe:
      issue.create_comment(safety_error)
      sys.exit(1)
  ```

### 2.2 设计原则

**安全分层**：
- **Stage 1（轻量校验）**：快速拒绝明显真实密钥，4 种常见前缀，`sys.exit(1)` 拒绝
- **Stage 5（完整校验）**：最终安全网，完整安全规则，`raise ValueError()` 回滚

**占位符保护**：
- 逻辑顺序：危险检查 → 安全检查 → 通过
- 避免误杀：`ghp_xxxxxxxxxxxxx` 被拒绝，`your-zhipu-api-key-here` 通过

---

## 3. 实施记录

### 3.1 代码变更

**功能提交**：
- SHA：`06c7a13`
- 消息：`feat(stage8.4): add Stage 1 secret precheck`
- 分支：`test/zhipu-stage8.4`
- 变更：`.github/scripts/agent_issue_handler.py`（+167 行）

**合并记录**：
- PR #46：`test/zhipu-stage8.4` → `main`
- Merge commit：`9a552ea`
- 合并日期：2026-04-27

---

## 4. 真实 Issue 验证记录

### 4.1 验证概述

**验证日期**：2026-04-27
**验证方式**：真实 GitHub Issue + Stage 1 触发
**验证目标**：确认 Stage 1 敏感内容前置识别功能正常工作

### 4.2 验证结果

| Issue # | 测试目标 | 追加内容 | 预期结果 | 实际结果 |
|---------|---------|---------|---------|---------|
| #47 | `sk-` 前缀拒绝 | `OPENAI_API_KEY=sk-abc123def456` | 拒绝，输出错误提示 | ✅ 通过 |
| #48 | `ghp_` 前缀拒绝 | `GITHUB_TOKEN=ghp_xxxxxxxxxxxxx` | 拒绝，输出错误提示 | ✅ 通过 |
| #49 | 安全占位符允许 | `ZHIPU_API_KEY=your-zhipu-api-key-here` | 通过，生成 Fix Plan | ✅ 通过 |
| #50 | 示例值允许 | `EXAMPLE_CONFIG=example_value` | 通过，生成 Fix Plan | ✅ 通过 |

### 4.3 验证结论

✅ **所有验证案例通过**

- **危险前缀检测**：`sk-`、`ghp_` 前缀被正确拒绝，输出结构化错误提示
- **安全占位符保护**：`your-zhipu-api-key-here`、`example_value` 被正确允许，生成 Fix Plan
- **验证时机正确**：在 Stage 1 plan 生成后立即执行
- **错误提示清晰**：明确指出检测到的前缀类型和可能原因

---

## 5. 测试覆盖情况

### 5.1 单元测试

**测试文件**：`.github/scripts/test_stage8_2_validation.py`

**新增测试用例**（13 个）：
1. `test_extract_append_content_success()` - 提取成功
2. `test_extract_append_content_no_section()` - 无目标章节
3. `test_extract_append_content_no_code_block()` - 无代码块
4. `test_validate_safety_sk_prefix()` - `sk-` 前缀拒绝
5. `test_validate_safety_ghp_prefix()` - `ghp_` 前缀拒绝
6. `test_validate_safety_github_pat_prefix()` - `github_pat_` 前缀拒绝
7. `test_validate_safety_aiza_prefix()` - `AIza` 前缀拒绝
8. `test_validate_safety_your_zhipu_placeholder()` - `your-zhipu-api-key-here` 允许
9. `test_validate_safety_example_value()` - `example_value` 允许
10. `test_validate_safety_your_api_key_here()` - `your-api-key-here` 允许
11. `test_validate_safety_xxx_placeholder()` - `xxx` 允许
12. `test_validate_safety_non_append_only()` - 非 append-only 跳过
13. `test_validate_safety_empty_plan()` - 空 plan 跳过

**运行命令**：
```bash
uv run python .github/scripts/test_stage8_2_validation.py
```

**测试结果**：✅ **31 个测试用例全部通过**（18 个现有 + 13 个新增）

### 5.2 集成测试

| 测试类型 | 测试数量 | 状态 |
|---------|---------|------|
| 单元测试 | 31 个 | ✅ 全部通过 |
| 集成测试（真实 Issue） | 4 个 | ✅ 全部通过 |
| **总计** | **35 个** | **✅ 全部通过** |

---

## 6. 当前限制

### 6.1 功能限制

1. **只检测 append-only 任务**
   - 非 append-only 任务（如 Markdown 修改）不触发检测
   - 原因：当前只有 append-only 模式有明确的追加内容格式

2. **只检测常见密钥前缀**
   - 检测范围：`sk-`、`ghp_`、`github_pat_`、`AIza`
   - 不检测其他格式（如 `Bearer`、`Basic`）
   - 原因：平衡安全性和可用性

3. **占位符列表不完整**
   - 当前安全列表包含 7 个常见占位符
   - 风险：低（用户可以调整 Issue 内容）

### 6.2 使用注意事项

1. **Stage 5 仍然是最终安全网**：Stage 1 轻量校验可能被绕过，必须保留 Stage 5 完整校验
2. **错误提示需要用户理解**：当前包含英文技术术语（API key、personal access token）
3. **非 append-only 任务不受保护**：Markdown 文件修改任务不触发检测

---

## 7. 后续建议

### 7.1 短期优化（可选）

**优先级：低**

1. 扩展检测前缀（`Bearer`、`Basic`、`AKIA`）
2. 优化错误提示（提供详细说明和修复建议）
3. 添加更多安全占位符

### 7.2 Stage 8.4 后续步骤

**Stage 8.4 Step 2：EOF newline 处理优化**（待确认）

- 目标：确保 append-only 追加内容后始终有换行符，避免多个追加内容连接在同一行
- 实施建议：在 `agent_issue_executor.py` 的 `append_to_file()` 函数中增加 newline 处理

### 7.3 中长期扩展（需谨慎评估）

**优先级：待评估**

1. 扩展到所有任务类型（为 Markdown 文件修改任务增加检测）
2. 增加机器学习检测（使用 AI 模型检测疑似密钥）
3. 用户自定义安全规则（允许仓库维护者自定义危险前缀列表）

---

## 8. 阶段结论

### 8.1 完成情况

Stage 8.4 Step 1 **完全达成**既定目标：

- ✅ 在 Stage 1 验证流程中检测追加内容安全性
- ✅ 拒绝常见密钥前缀（`sk-`、`ghp_`、`github_pat_`、`AIza`）
- ✅ 允许安全占位符（`your-zhipu-api-key-here`、`example_value` 等）
- ✅ 保持 Stage 5 的完整安全校验作为最终安全网
- ✅ 通过 4 个真实 Issue 验证功能正常
- ✅ 通过 31 个单元测试验证代码逻辑

### 8.2 核心价值

**安全价值**：
- 前移安全检查：从 Stage 5 前移到 Stage 1，更早发现风险
- 减少无效计划：避免生成包含敏感内容的 Fix Plan
- 保持双重保护：Stage 1 轻量校验 + Stage 5 完整校验

**用户体验价值**：
- 更快的反馈：用户在 Stage 1 就知道追加内容不安全
- 更清晰的错误提示：明确指出检测到的密钥前缀类型
- 更好的可用性：安全占位符不会被误杀

**技术价值**：
- 代码结构清晰：两个独立函数，职责单一
- 测试覆盖充分：单元测试 + 集成测试，35 个测试用例
- 向后兼容：不影响现有功能，Stage 5 完整保留

### 8.3 与 Stage 8.3 的关系

**Stage 8.3**：
- 目标：Stage 1 Prompt 增强，强制 append-only 计划标准格式
- 完成：部分完成（只做了 Prompt 增强，未做敏感内容识别）
- 留待后续：Stage 1 敏感内容识别（见 `STAGE8_3_COMPLETE.md` 第 6.1 节）

**Stage 8.4 Step 1**：
- 目标：实施 Stage 1 敏感内容识别
- 完成：完全达成
- 是 Stage 8.3 留待后续内容的延续和完成

---

## 9. 相关文档

- **Stage 8.3 完成记录**：`STAGE8_3_COMPLETE.md`
- **Stage 8.2 完成记录**：`STAGE8_2_COMPLETE.md`
- **使用指南**：`ZHIPU_AGENT_USAGE.md`
- **文档导航**：`ZHIPU_GUIDE.md`
- **PR Review 清单**：`PR_REVIEW_CHECKLIST.md`

---

**文档维护**：@yyd841122
**最后更新**：2026-04-27

---

**Stage 8.4 Step 1 完成** 🎯

**核心成果**：Stage 1 敏感内容前置识别，提前拒绝疑似真实密钥，保持双重安全保护
