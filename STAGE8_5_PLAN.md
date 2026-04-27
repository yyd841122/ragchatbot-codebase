# Stage 8.5 规划文档

**规划日期**：2026-04-27
**版本**：v1.0（精简版）
**前置阶段**：Stage 8.4 Step 1（敏感内容前置识别）

---

## 1. 阶段定位

**Stage 8.5：边界测试补充与文档一致性梳理**

**核心定位**：
- ❌ **不扩展新文件类型**
- ❌ **不做大功能开发**
- ✅ **巩固已有成果**
- ✅ **补充必要测试**
- ✅ **梳理文档一致性**
- ✅ **降低维护成本**

**设计理念**：
> **小步迭代，先稳定再扩展**

---

## 2. 背景与问题来源

### 2.1 Stage 8.4 Step 1 完成情况

Stage 8.4 Step 1 已于 2026-04-27 完成，核心成果：
- ✅ 新增 Stage 1 敏感内容前置识别能力（`validate_plan_append_content_safety()`）
- ✅ 两层防御体系已建立（Stage 1 轻量校验 + Stage 5 完整校验）
- ✅ 通过 4 个真实 Issue 验证（#47、#48、#49、#50）
- ✅ 通过 31 个单元测试

### 2.2 当前存在的问题

**测试覆盖不足**：缺少 `.gitignore`、`.env.example`、Stage 1 敏感内容检测的边界测试

**文档可能不一致**：`ZHIPU_GUIDE.md`、`ZHIPU_AGENT_USAGE.md`、`PR_REVIEW_CHECKLIST.md` 可能未同步 Stage 8.4 能力

**后续扩展准备不足**：缺少量化的使用数据和失败率统计

### 2.3 为什么不做 Stage 9（扩展文件类型）

**当前已支持范围已够用**：Markdown 文件（根目录和一级子目录）+ 配置文件（根目录 `.gitignore`、`.env.example`，append-only）

**扩展文件类型的风险**：`requirements.txt`（恶意依赖风险）、`.yaml`/`.toml`/`.ini`（格式复杂、解析器依赖）、维护成本显著上升

**结论**：应该先巩固 Stage 8.4 Step 1 成果，补充测试和梳理文档，为未来 Stage 9 做准备，而不是急于扩展。

---

## 3. 当前已具备能力

### 3.1 文件类型支持

| 文件类型 | 路径范围 | 操作模式 | 状态 |
|---------|---------|---------|------|
| Markdown 文件（.md） | 根目录和一级子目录 | 完整内容修改 | ✅ 稳定 |
| `.gitignore` | 仅根目录 | append-only 追加 | ✅ 稳定 |
| `.env.example` | 仅根目录 | append-only 追加 | ✅ 稳定 |

### 3.2 安全防护能力（两层防御）

**Stage 1（轻量校验）**：检测追加内容安全性、拒绝常见密钥前缀（`sk-`、`ghp_`、`github_pat_`、`AIza`）、允许安全占位符

**Stage 5（完整校验）**：路径安全检查、追加内容安全验证、格式验证、重复规则检测、内容长度限制

### 3.3 文档与测试

**完成记录文档**：`STAGE6_COMPLETE.md`、`STAGE7_*_TEST_RESULT.md`、`STAGE8_2_COMPLETE.md`、`STAGE8_3_COMPLETE.md`、`STAGE8_4_STEP1_COMPLETE.md`

**测试覆盖**：31 个单元测试 + 4 个真实 Issue 验证

---

## 4. 当前仍需巩固的问题

### 4.1 测试覆盖不足

**`.gitignore` 边界测试缺失**：超长内容（100 行边界）、超长单行（1000 字符边界）、空内容、空白字符、特殊字符

**`.env.example` 边界测试缺失**：小写变量名、包含空格的变量名、多行值、空变量名

**Stage 1 敏感内容检测边界测试缺失**：多个前缀组合、混合占位符和真实前缀、非 append-only 任务跳过

### 4.2 文档可能不一致

**需要检查的文档**：`ZHIPU_GUIDE.md`、`ZHIPU_AGENT_USAGE.md`、`PR_REVIEW_CHECKLIST.md`、`STAGE8_3_COMPLETE.md`

### 4.3 后续扩展准备不足

**缺少量化的使用数据**：Stage 1 触发次数和失败率、Stage 5 执行次数和安全拦截次数、用户反馈的问题列表

**建议**：Stage 8.5 完成后，观察 1-2 周实际使用情况，收集数据，为 Stage 9 决策提供支撑。

---

## 5. Stage 8.5 目标

### 5.1 核心目标

1. **巩固 Stage 8.4 Step 1 成果**：补充边界测试用例，验证两层防御体系
2. **梳理文档一致性**：确保所有文档同步最新能力，清理过时内容
3. **为后续扩展做准备**：完善测试覆盖，为 Stage 9 是否扩展文件类型提供数据支撑

---

## 6. 最小可执行范围

### 6.1 边界测试补充

**新增 14 个测试用例**：

**`.gitignore` 边界测试（5 个）**：超长内容、超长单行、空内容、空白字符、特殊字符

**`.env.example` 边界测试（5 个）**：小写变量名、包含空格的变量名、多行值、空变量名、非法字符

**Stage 1 敏感内容检测边界测试（4 个）**：多个前缀组合、混合占位符和真实前缀、非 append-only 任务跳过、空 plan 跳过

**运行命令**：`uv run python .github/scripts/test_stage8_2_validation.py`

**预期结果**：45 个测试用例全部通过（31 个现有 + 14 个新增）

### 6.2 文档一致性梳理

**更新 `ZHIPU_GUIDE.md`**：确认"当前已支持能力"章节与最新能力一致，更新"测试记录"表格，清理过时内容

**更新 `ZHIPU_AGENT_USAGE.md`**：补充 Stage 8.4 Step 1 说明，更新"当前支持范围"章节，更新"常见失败原因"章节

**更新 `PR_REVIEW_CHECKLIST.md`**：确认"配置文件 append-only 支持"检查项与当前能力一致

**检查 `STAGE8_3_COMPLETE.md`**：检查"留待后续"内容是否已实施，标记已完成的内容，删除或更新未实施的内容

---

## 7. 明确不做的范围

### 7.1 不扩展新文件类型

- ❌ **不支持 `requirements.txt`**：安全风险高，用户需求不强
- ❌ **不支持 `.yaml`、`.json`、`.toml`、`.ini`**：格式复杂、解析器依赖、安全风险高
- ❌ **不支持代码文件修改**（`.py`、`.js`、`.yml` 等）

### 7.2 不做大功能开发

- ❌ **不做 EOF newline 代码优化**：优先级低，收益不明确
- ❌ **不改 GitHub Actions workflow**：当前 workflow 稳定
- ❌ **不大改 Stage 1 prompt**：Stage 8.3 已完成基础增强
- ❌ **不重构核心脚本**（`agent_issue_handler.py`、`agent_issue_executor.py`）：当前代码可维护
- ❌ **不新建 `agent_common.py`**：当前代码结构清晰
- ❌ **不做自动合并 PR**：必须人工 review
- ❌ **不做自动关闭 Issue**：由人工决定是否关闭

### 7.3 暂缓错误提示优化

**原因**：可能影响范围较多，当前 Stage 1 和 Stage 5 已能正确拒绝，应先补测试和梳理文档，再决定是否改提示逻辑

**建议**：作为"后续建议"记录在 Stage 8.5 完成文档中，留待 Stage 8.6 或后续阶段评估。

---

## 8. 涉及文件

### 8.1 测试文件

**文件路径**：`.github/scripts/test_stage8_2_validation.py`

**修改内容**：新增 14 个测试用例（.gitignore 5 个、.env.example 5 个、Stage 1 敏感内容检测 4 个）

### 8.2 文档文件

**文件路径**：`ZHIPU_GUIDE.md`、`ZHIPU_AGENT_USAGE.md`、`PR_REVIEW_CHECKLIST.md`、`STAGE8_3_COMPLETE.md`

**修改内容**：轻量更新（不改动结构），更新"当前支持范围"描述，补充 Stage 8.4 Step 1 说明，清理过时内容

### 8.3 新增文档

**文件路径**：`STAGE8_5_COMPLETE.md`（Stage 8.5 完成后创建）

**内容**：记录 Stage 8.5 完成情况、新增测试用例、文档更新内容、后续建议（包括错误提示优化）

---

## 9. 建议任务拆解

### Step 1：边界测试补充（1-2天）

**任务目标**：补充边界测试用例，提升测试覆盖率

**具体任务**：
1. 新增 14 个测试用例（.gitignore 5 个、.env.example 5 个、Stage 1 敏感内容检测 4 个）
2. 运行所有测试，确保通过
3. 提交测试代码

**验收标准**：所有新增测试用例通过，无回归问题

---

### Step 2：文档一致性梳理（1-2天）

**任务目标**：确保所有文档同步最新能力，清理过时内容

**具体任务**：
1. 更新 `ZHIPU_GUIDE.md`、`ZHIPU_AGENT_USAGE.md`、`PR_REVIEW_CHECKLIST.md`
2. 检查 `STAGE8_3_COMPLETE.md`，标记已完成内容
3. 提交文档更新

**验收标准**：所有文档描述一致，无过时或矛盾内容

---

### Step 3：创建完成记录文档（0.5天）

**任务目标**：记录 Stage 8.5 完成情况

**具体任务**：
1. 创建 `STAGE8_5_COMPLETE.md`
2. 记录新增测试用例、文档更新内容
3. 提供后续建议（包括错误提示优化）
4. 更新 `ZHIPU_GUIDE.md` 测试记录索引

**验收标准**：文档结构清晰，内容完整，与之前完成记录文档风格一致

---

## 10. 测试方案

**测试文件**：`.github/scripts/test_stage8_2_validation.py`

**新增测试用例**（14 个）：

**`.gitignore` 边界测试（5 个）**：
1. `test_validate_gitignore_too_many_lines()` - 超过 100 行应被拒绝
2. `test_validate_gitignore_line_too_long()` - 单行超过 1000 字符应被拒绝
3. `test_validate_gitignore_empty_content()` - 空内容应被拒绝
4. `test_validate_gitignore_whitespace_only()` - 只有空白字符应被拒绝
5. `test_validate_gitignore_special_chars()` - 包含 Unicode 和控制字符

**`.env.example` 边界测试（5 个）**：
1. `test_validate_env_lowercase_varname()` - 小写变量名应被拒绝
2. `test_validate_env_varname_with_spaces()` - 包含空格的变量名应被拒绝
3. `test_validate_env_multiline_value()` - 多行值应被拒绝
4. `test_validate_env_empty_varname()` - 空变量名应被拒绝
5. `test_validate_env_invalid_chars()` - 非法字符应被拒绝

**Stage 1 敏感内容检测边界测试（4 个）**：
1. `test_validate_safety_multiple_prefixes()` - 多个前缀组合测试
2. `test_validate_safety_mixed_prefix_and_placeholder()` - 混合占位符和真实前缀
3. `test_validate_safety_non_append_only_skipped()` - 非 append-only 任务跳过
4. `test_validate_safety_empty_plan_skipped()` - 空 plan 跳过

**建议**：Stage 8.5 期间不新增真实 Issue 测试，依赖 Stage 8.4 Step 1 的 4 个验证 Issue 即可。

---

## 11. 文档梳理方案

参考第 6.2 节"文档一致性梳理"的详细内容。

---

## 12. 风险点

### 12.1 测试补充风险

**风险**：新增测试用例可能发现现有代码的 bug

**应对措施**：优先修复发现的 bug，如 bug 严重，考虑推迟 Stage 8.5 完成；如 bug 轻微，记录在"已知问题"中

### 12.2 文档更新风险

**风险**：文档梳理可能引入不一致或错误

**应对措施**：更新后仔细核对，如不确定，保持原有描述不变，在 `STAGE8_5_COMPLETE.md` 中记录所有更新内容

### 12.3 范围蔓延风险

**风险**：Stage 8.5 可能演变成大范围开发

**应对措施**：严格遵循"最小可执行范围"，不扩展新文件类型，不做 EOF newline 代码优化，不大改 prompt，不重构核心脚本

---

## 13. 验收标准

### 13.1 测试覆盖

- ✅ 新增 14 个测试用例，全部通过
- ✅ 无回归问题（现有 31 个测试用例仍通过）

### 13.2 文档一致性

- ✅ `ZHIPU_GUIDE.md` 描述与最新能力一致
- ✅ `ZHIPU_AGENT_USAGE.md` 包含 Stage 8.4 Step 1 说明
- ✅ `PR_REVIEW_CHECKLIST.md` 检查项与当前能力一致
- ✅ `STAGE8_3_COMPLETE.md` 标记已完成内容
- ✅ 无过时或矛盾内容

### 13.3 完成记录

- ✅ 创建 `STAGE8_5_COMPLETE.md`
- ✅ 记录新增测试用例、文档更新内容
- ✅ 提供后续建议（包括错误提示优化）

---

## 14. 推荐执行顺序

### 顺序 1：先测试，后文档（推荐）

**原因**：测试补充可能发现 bug，需要先修复 bug，再更新文档

**执行顺序**：
1. Step 1：边界测试补充（1-2天）
2. Step 2：文档一致性梳理（1-2天）
3. Step 3：创建完成记录文档（0.5天）

**总时间**：2.5-4.5天

---

### 后续观察期（可选）

**建议**：Stage 8.5 完成后，观察 1-2 周实际使用情况

**收集数据**：Stage 1 触发次数和失败率、Stage 5 执行次数和安全拦截次数、用户反馈的问题列表

**目的**：为 Stage 9 是否扩展文件类型提供数据支撑

---

## 15. 阶段结论

### 15.1 Stage 8.5 定位

**Stage 8.5：边界测试补充与文档一致性梳理**

**核心定位**：❌ 不扩展新文件类型，❌ 不做大功能开发，✅ 巩固已有成果，✅ 补充必要测试，✅ 梳理文档一致性，✅ 降低维护成本

### 15.2 预期收益

1. **测试覆盖更完善**：补充边界测试用例，提升测试覆盖率
2. **文档更一致**：所有文档同步最新能力，降低维护成本
3. **为后续扩展做准备**：完善的测试和文档为 Stage 9 打下基础

### 15.3 与 Stage 8.4 的关系

**Stage 8.4 Step 1**：目标为 Stage 1 敏感内容前置识别，完成度 100%，留待后续包括 EOF newline 优化、错误提示优化

**Stage 8.5**：目标为巩固 Stage 8.4 Step 1 成果，范围为边界测试补充 + 文档一致性梳理，留待后续包括错误提示优化、Stage 9 扩展文件类型

### 15.4 后续建议

**Stage 8.5 完成后，建议观察 1-2 周实际使用情况**：

1. **收集数据**：Stage 1 触发次数和失败率、Stage 5 执行次数和安全拦截次数、用户反馈的问题列表

2. **评估后续方向**：
   - 如边界问题频发 → 考虑 Stage 8.6：错误提示优化
   - 如用户强烈需求 → 考虑 Stage 9：扩展 `requirements.txt` 支持
   - 如系统稳定 → 继续观察，暂不开发新功能

3. **保持小步迭代**：每个阶段范围明确，不蔓延；先稳定，再扩展；有问题及时修复

### 15.5 相关文档

详细参考：`STAGE8_4_STEP1_COMPLETE.md`、`STAGE8_3_COMPLETE.md`、`STAGE8_2_COMPLETE.md`、`ZHIPU_AGENT_USAGE.md`、`ZHIPU_GUIDE.md`、`PR_REVIEW_CHECKLIST.md`

---

**文档维护**：@yyd841122
**最后更新**：2026-04-27

---

**Stage 8.5 规划完成** 📋

**核心原则**：小步迭代，先稳定再扩展，不扩展新文件类型
