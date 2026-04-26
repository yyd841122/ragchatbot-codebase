#!/usr/bin/env python3
"""
Zhipu Issue Agent Handler

当用户在 GitHub Issue 中评论 @zhipu 时触发。
读取 Issue 上下文，调用智谱 AI 生成结构化的执行计划，并评论回 Issue。
"""

import os
import sys
from typing import Optional

import zhipuai
from github import Github


def is_safe_path(file_path: str) -> bool:
    """检查路径是否安全

    规则：
    - 空路径返回 False
    - 绝对路径（以 / 开头）返回 False
    - 禁止 '../' 相对路径跳转
    - 路径按 '/' 分隔后最多 2 段

    Args:
        file_path: 文件路径

    Returns:
        路径是否安全
    """
    # 空路径检查
    if not file_path or not file_path.strip():
        return False

    # 绝对路径检查（以 / 开头）
    if file_path.startswith('/'):
        return False

    # 禁止相对路径跳转
    if '../' in file_path:
        return False

    # 统一路径分隔符
    normalized = file_path.replace('\\', '/')

    # 检查深度（按 / 分隔后最多 2 段）
    parts = normalized.split('/')
    return len(parts) <= 2


def is_supported_markdown_file(file_path: str) -> bool:
    """检查是否为支持的 Markdown 文件

    规则：
    - 必须以 .md 结尾
    - 路径必须安全（调用 is_safe_path）

    Args:
        file_path: 文件路径

    Returns:
        是否为支持的 Markdown 文件
    """
    # 必须以 .md 结尾
    if not file_path.lower().endswith('.md'):
        return False

    # 路径安全检查
    return is_safe_path(file_path)


def is_supported_append_only_config_file(file_path: str) -> bool:
    """检查是否为支持的 append-only 配置文件

    规则：
    - 只支持 .gitignore 和 .env.example
    - 必须在根目录（路径按 / 分隔后只有 1 段）
    - 路径必须安全（调用 is_safe_path）

    Args:
        file_path: 文件路径

    Returns:
        是否为支持的 append-only 配置文件
    """
    # 统一路径格式
    normalized = file_path.replace('\\', '/')

    # 提取 basename
    basename = normalized.split('/')[-1].lower()

    # 检查是否为支持的配置文件
    supported_config_files = ['.gitignore', '.env.example']
    if basename not in supported_config_files:
        return False

    # 必须在根目录（路径按 / 分隔后只有 1 段）
    if len(normalized.split('/')) != 1:
        return False

    # 路径安全检查
    return is_safe_path(file_path)


def get_env_var(var_name: str) -> str:
    """获取环境变量，如果不存在则退出"""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ 环境变量 {var_name} 未设置", file=sys.stderr)
        sys.exit(1)
    return value


def should_process_comment(comment_body: str) -> bool:
    """检查评论是否包含 @zhipu"""
    return "@zhipu" in comment_body


def get_recent_comments(issue, max_comments: int = 5) -> list[str]:
    """获取最近的评论，并尽量过滤 bot 评论与已有计划评论"""
    try:
        comments = list(issue.get_comments())
        recent_comments = comments[-max_comments:] if comments else []

        result = []
        for comment in recent_comments:
            user = comment.user.login
            body = comment.body or ""

            if user.endswith("[bot]"):
                continue

            if "## 🤖 Zhipu Fix Plan" in body:
                continue

            result.append(f"@{user}: {body}")

        return result
    except Exception as e:
        print(f"⚠️ 获取评论失败: {e}")
        return []


def build_context_prompt(
    issue_title: str,
    issue_body: str,
    trigger_comment: str,
    recent_comments: list[str],
) -> str:
    """构建发送给智谱 AI 的提示词"""

    comments_text = "\n".join(recent_comments) if recent_comments else "（无其他评论）"

    prompt = f"""你是一个资深 GitHub Actions + Python 自动化工程师 + AI Agent 架构师。

请根据以下 GitHub Issue 信息，生成一份结构化的执行计划（Todo List）。

## Issue 信息

**标题**: {issue_title}

**正文**:
{issue_body}

**触发评论**:
{trigger_comment}

**最近评论**:
{comments_text}

---

请生成一份中文的执行计划，格式如下：

```markdown
## 🤖 Zhipu Fix Plan

### 问题理解
[简洁总结这个 Issue 要解决的问题]

### 计划修改文件
- `README.md` - [修改目的]

### Todo List
- [ ] [第一步] - [预期结果]
- [ ] [第二步] - [预期结果]
- [ ] [第三步] - [预期结果]
- [ ] [第四步] - [预期结果]
- [ ] [第五步] - [预期结果]

### 风险提示
- [可能的风险点1]
- [可能的风险点2]

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段（第二阶段功能，敬请期待）

---
🤖 本回复由 Zhipu AI 生成 - {os.getenv('REPO', '')}
```

要求：

Todo List 要具体、可执行、可验证
每个步骤应该是独立的、可以单独验证的
优先给出"最小可行方案"，避免过度设计
文件路径要基于项目根目录，使用相对路径

**支持的文件类型**：
- ✅ Markdown 文档文件（.md）
  - 根目录的 .md 文件（如 `README.md`、`CHANGELOG.md`）
  - 一级子目录的 .md 文件（如 `docs/GUIDE.md`、`docs/FAQ.md`）
- ✅ 配置文件（仅 append-only 模式）
  - `.gitignore` - 在文件末尾追加新的忽略规则
  - `.env.example` - 在文件末尾追加新的环境变量示例

**路径规则**：
- 路径按 `/` 分隔后最多 2 段
- 禁止相对路径跳转（如 `../file.md`）
- 文件路径必须真实存在于仓库中

**配置文件使用说明**：
- `.gitignore` 和 `.env.example` 只支持 append-only 模式
- 不能修改或删除现有内容，只能在末尾追加新内容
- AI 会自动生成要追加的内容片段

### Append-Only 配置文件计划格式要求

如果计划修改的文件是 `.gitignore` 或 `.env.example`，**必须**按以下格式输出计划：

**示例 1**：修改 .gitignore
```markdown
### 计划修改文件
- `.gitignore` - 追加忽略规则

### 操作类型
- append-only（追加模式）

### 计划追加内容
```gitignore
*.stage82.log
```
```

**示例 2**：修改 .env.example
```markdown
### 计划修改文件
- `.env.example` - 追加环境变量示例

### 操作类型
- append-only（追加模式）

### 计划追加内容
```env
STAGE82_TEST_KEY=example_value
```
```

**重要要求**：
1. **必须包含 `### 操作类型` 章节**，明确标注 "append-only"
2. **必须包含 `### 计划追加内容` 章节**，内容放在代码块中
3. 代码块语言标记：
   - `.gitignore` 使用 ```gitignore
   - `.env.example` 使用 ```env
4. `.env.example` 的值**必须是安全的占位符**：
   - ✅ 正确：`API_KEY=your_api_key_here`、`SECRET_KEY=example_value`
   - ❌ 错误：`API_KEY=sk-xxxx`、`GITHUB_TOKEN=ghp_xxxx`、`GOOGLE_API_KEY=AIzaxxxx`
5. **安全检测**：如果用户请求追加疑似真实密钥（如 `sk-`、`ghp_`、`github_pat_`、`AIza` 等前缀），**必须在 Stage 1 计划中拒绝**：
   ```markdown
   ### 安全判断
   拒绝执行（包含疑似真实密钥）

   ### 操作类型
   reject

   ### 计划修改文件
   无

   ### 计划追加内容
   无

   ### 拒绝原因
   检测到疑似真实密钥前缀：sk-。请使用安全的占位符（如 your_api_key_here）。
   ```

**强制要求**（append-only 配置文件任务必须遵守）：

当计划修改的文件是 `.gitignore` 或 `.env.example` 时，**必须**按照以下固定结构输出计划：

```markdown
### 计划修改文件
- [文件名] - [修改目的]

### 操作类型
append-only

### 计划追加内容
```[gitignore|env]
[用户明确要求追加的内容]
```

### Todo List
- [ ] 第一步：读取 [文件名] 当前内容
- [ ] 第二步：追加新内容到文件末尾
- [ ] 第三步：创建 commit
- [ ] 第四步：创建 Draft PR

### 风险提示
- [可能的风险点]

### 下一步
💡 评论 `/zhipu-apply` 可进入执行阶段
```

**禁止行为**（必须遵守）：
1. ❌ **禁止**只输出 `Todo List`，必须先输出 `### 操作类型` 和 `### 计划追加内容`
2. ❌ **禁止**省略 `### 操作类型` 章节
3. ❌ **禁止**省略 `### 计划追加内容` 章节
4. ❌ **禁止**在 `### 计划追加内容` 中放置解释文字，只能放要追加的原始内容
5. ❌ **禁止**替换用户明确给出的追加内容，必须优先使用用户给出的原始内容

**`### 计划追加内容` 格式要求**：
- **必须**使用 fenced code block（三个反引号包围）
- 代码块语言标记：
  - `.gitignore` 使用 ```gitignore
  - `.env.example` 使用 ```env
- 代码块内**只包含要追加的内容**，不包含任何解释或说明
- 如果用户在 Issue 中明确给出了追加内容（如代码块或明文），**必须**使用用户给出的内容，不要替换成 AI 自己生成的内容

**示例对比**：

✅ **正确（包含所有必需章节）**：
```markdown
### 计划修改文件
- `.gitignore` - 追加忽略规则

### 操作类型
append-only

### 计划追加内容
```gitignore
*.stage83.log
```

### Todo List
- [ ] 读取 .gitignore 当前内容
- [ ] 追加 *.stage83.log 到文件末尾
- [ ] 创建 commit
- [ ] 创建 Draft PR
...
```

❌ **错误（缺少必需章节）**：
```markdown
### 计划修改文件
- `.gitignore` - 追加忽略规则

### Todo List
- [ ] 读取 .gitignore
- [ ] 追加 *.stage83.log
...
```
（缺少 `### 操作类型` 和 `### 计划追加内容` 章节）

❌ **错误（追加内容包含解释）**：
```markdown
### 计划追加内容
```gitignore
# 追加以下规则
*.stage83.log
```
```
（代码块内包含了解释文字 `# 追加以下规则`）

❌ **错误（替换了用户给出的内容）**：
用户要求追加 `*.stage83.log`，但 AI 生成：
```markdown
### 计划追加内容
```gitignore
*.log
*.tmp
```
```
（应该使用用户给出的 `*.stage83.log`，不要替换成 AI 自己生成的内容）

**不支持的文件类型**：
- 代码文件（.py, .js, .yml 等）
- 其他配置文件（requirements.txt 等）

用简洁的中文描述
如果信息不足，请明确写"信息不足"，不要编造不存在的实现细节

请只返回 Markdown 格式的计划内容，不要包含其他解释。
"""
    return prompt


def call_zhipu_api(prompt: str) -> Optional[str]:
    """调用智谱 AI 生成回复"""
    try:
        api_key = get_env_var("ZHIPU_API_KEY")
        client = zhipuai.ZhipuAI(api_key=api_key)

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            return content.strip() if content else None

        print("❌ 智谱 API 返回了空响应", file=sys.stderr)
        return None

    except Exception as e:
        print(f"❌ 调用智谱 API 失败: {e}", file=sys.stderr)
        return None


def normalize_plan_response(ai_response: str) -> str:
    """确保计划回复至少带有统一标题"""
    if "## 🤖 Zhipu Fix Plan" not in ai_response:
        return f"## 🤖 Zhipu Fix Plan\n\n{ai_response}"
    return ai_response


def extract_first_file_path(plan: str) -> str:
    """从 Stage 1 计划中提取第一个文件路径

    Args:
        plan: Stage 1 计划的完整内容

    Returns:
        str: 第一个文件路径，如果未找到则返回空字符串
    """
    if not plan:
        return ""

    # 查找"计划修改文件"章节
    lines = plan.split('\n')
    in_target_section = False

    for line in lines:
        # 检测是否进入目标章节
        if "### 计划修改文件" in line:
            in_target_section = True
            continue

        # 如果进入目标章节，开始提取文件路径
        if in_target_section:
            # 跳过空行
            if not line.strip():
                continue

            # 遇到下一个章节标题，停止查找
            if line.strip().startswith('###'):
                break

            # 尝试提取文件路径（支持多种格式）
            # 格式1: Markdown 列表: - `README.md`
            # 格式2: 仅反引号: `README.md`
            # 格式3: 普通文本: README.md

            # 去除 Markdown 列表符号
            cleaned_line = line.strip()
            if cleaned_line.startswith('- '):
                cleaned_line = cleaned_line[2:].strip()

            # 去掉包裹的反引号
            if '`' in cleaned_line:
                # 提取第一个反引号对内的内容
                start = cleaned_line.find('`')
                end = cleaned_line.find('`', start + 1)
                if start != -1 and end != -1:
                    cleaned_line = cleaned_line[start + 1:end].strip()

            # 检查是否存在 " - [" 分隔符（路径 + 说明格式）
            if ' - [' in cleaned_line:
                cleaned_line = cleaned_line.split(' - [', 1)[0].strip()

            # 最终再 strip 一次确保干净
            cleaned_line = cleaned_line.strip()

            # 如果提取到有效内容，返回
            if cleaned_line and not cleaned_line.startswith('*') and not cleaned_line.startswith('#'):
                return cleaned_line

    return ""


def validate_first_file_exists(plan: str, repo) -> tuple[bool, str]:
    """验证计划中的第一个文件是否真实存在且符合规则

    Args:
        plan: AI 生成的计划
        repo: Github repository 对象

    Returns:
        tuple[bool, str]: (是否通过, 错误信息)
    """
    # 提取第一个文件路径
    first_file = extract_first_file_path(plan)

    if not first_file:
        return False, "计划中未找到文件路径，请检查计划格式"

    # 检查是否为支持的文件类型（Markdown 或配置文件）
    is_markdown = is_supported_markdown_file(first_file)
    is_config = is_supported_append_only_config_file(first_file)

    if not is_markdown and not is_config:
        return False, f"""文件 `{first_file}` 不在当前支持范围内。

**当前支持的文件类型**：
- ✅ 根目录的 `.md` 文件（如 `README.md`、`CHANGELOG.md`）
- ✅ 一级子目录的 `.md` 文件（如 `docs/GUIDE.md`、`docs/FAQ.md`）
- ✅ 根目录的配置文件（仅 `.gitignore`、`.env.example`，append-only 模式）
- ❌ 不支持更深层的目录（如 `docs/deep/file.md`）
- ❌ 不支持其他文件类型（如 `.py`、`requirements.txt`）

**路径规则**：
- 路径按 `/` 分隔后最多 2 段
- 禁止相对路径跳转（如 `../file.md`）
- 禁止绝对路径（如 `/etc/file.md`）

请在 Issue 中重新评论 `@zhipu`，确保第一个文件符合上述规则。"""

    # 验证文件是否存在
    try:
        repo.get_contents(first_file)
        return True, ""
    except Exception:
        return False, f"文件 `{first_file}` 在仓库中不存在。请重新在 Issue 中评论 `@zhipu` 生成正确的计划。"


def extract_plan_append_content(plan: str) -> Optional[str]:
    """从 Stage 1 plan 的 ### 计划追加内容 章节中提取 fenced code block 内容

    Args:
        plan: Stage 1 生成的完整计划内容

    Returns:
        str: 提取的代码块内容，如果未找到则返回 None
    """
    if not plan:
        return None

    # 查找 "### 计划追加内容" 章节
    lines = plan.split('\n')
    in_target_section = False
    code_block_content = []
    in_code_block = False

    for line in lines:
        # 检测是否进入目标章节
        if "### 计划追加内容" in line:
            in_target_section = True
            continue

        # 如果进入目标章节，开始提取代码块
        if in_target_section:
            # 检测代码块开始
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    continue
                else:
                    # 代码块结束
                    break

            # 如果在代码块内，收集内容
            if in_code_block:
                code_block_content.append(line)

            # 遇到下一个章节标题，停止查找
            if line.strip().startswith('###') and not in_code_block:
                break

    # 如果找到代码块内容，返回
    if code_block_content:
        return '\n'.join(code_block_content).strip()

    return None


def validate_plan_append_content_safety(plan: str) -> tuple[bool, str]:
    """对 Stage 1 plan 中的 append-only 追加内容做轻量安全检查

    只做前置提醒和明显风险拦截。
    Stage 5 的 validate_append_content() 仍然是最终强校验。

    检查规则：
    1. 只针对包含 "### 操作类型" 和 "append-only" 的 plan
    2. 只针对包含 "### 计划追加内容" 的 plan
    3. 检测常见密钥前缀：sk-、ghp_、github_pat_、AIza
    4. 允许安全的占位符：your_*、example_*、test_*、dummy、placeholder、xxx

    Args:
        plan: Stage 1 生成的完整计划内容

    Returns:
        tuple[bool, str]: (是否通过, 错误信息)
    """
    if not plan:
        return True, ""  # 空 plan 允许通过（后续流程会处理）

    # 检查是否为 append-only 任务
    if "### 操作类型" not in plan:
        return True, ""  # 没有 "### 操作类型" 章节，不是 append-only 任务

    if "append-only" not in plan.lower():
        return True, ""  # 不是 append-only 任务

    # 提取追加内容
    append_content = extract_plan_append_content(plan)

    if not append_content:
        # 没有 "### 计划追加内容" 或没有代码块，允许通过（后续流程会处理）
        return True, ""

    # 转换为小写用于检测
    append_content_lower = append_content.lower()

    # 检测明显的真实密钥前缀
    dangerous_patterns = [
        ('sk-', 'OpenAI API key'),
        ('ghp_', 'GitHub personal access token'),
        ('github_pat_', 'GitHub personal access token (fine-grained)'),
        ('AIza', 'Google API key'),
    ]

    # 先检查危险前缀（如果有危险前缀，直接拒绝）
    for pattern, desc in dangerous_patterns:
        if pattern.lower() in append_content_lower:
            # 构建详细的错误提示
            error_msg = f"""## ⚠️ Stage 1 计划验证失败

**检测到疑似真实密钥**

追加内容中包含疑似真实密钥前缀：`{pattern}`（{desc}）

**安全提示**：
- ⚠️ 请不要把真实密钥写入 Issue、代码或 .env.example
- ⚠️ 真实密钥应该存储在本地 .env 文件中（已在 .gitignore 中）
- ⚠️ .env.example 应该只包含安全的占位符

**正确示例**：
```env
OPENAI_API_KEY=your_openai_api_key_here
ZHIPU_API_KEY=your-zhipu-api-key-here
GITHUB_TOKEN=your_github_token_here
GOOGLE_API_KEY=your_google_api_key_here
TEST_KEY=example_value
```

**请按以下步骤修正**：
1. 修改 Issue 内容，使用安全的占位符替换真实密钥
2. 重新评论 `@zhipu` 生成新的计划

---
🤖 由 Zhipu AI Stage 1 安全校验生成 | {os.getenv('REPO', '')}"""
            return False, error_msg

    # 如果没有危险前缀，再检查是否包含安全的占位符（作为额外验证）
    # 注意：这个检查只在调试时有用，实际逻辑是"没有危险前缀就允许"
    safe_placeholders = [
        'your_api_key_here',
        'your-openai-api-key-here',
        'your-zhipu-api-key-here',
        'your_',
        'example_value',
        'example-key',
        'placeholder',
        'test_key',
        'test-key',
        'dummy',
        'changeme',
        'replace',
    ]

    # 检查是否包含明显的占位符（仅用于日志，不影响结果）
    for placeholder in safe_placeholders:
        if placeholder.lower() in append_content_lower:
            # 包含明显的占位符，认为是安全的
            return True, ""

    # 未检测到明显的危险前缀，允许通过
    # 即使没有明显的占位符，也允许通过（可能是自定义的值）
    return True, ""


def main() -> None:
    """主函数"""
    print("🚀 Zhipu Issue Agent 启动...")

    github_token = get_env_var("GITHUB_TOKEN")
    repo_name = get_env_var("REPO")
    issue_number = int(get_env_var("ISSUE_NUMBER"))
    comment_body = get_env_var("COMMENT_BODY")
    comment_author = get_env_var("COMMENT_AUTHOR")

    print(f"📦 仓库: {repo_name}")
    print(f"📝 Issue: #{issue_number}")
    print(f"💬 评论者: @{comment_author}")

    if not should_process_comment(comment_body):
        print("⏭️ 评论不包含 @zhipu，跳过处理")
        return

    print("✅ 评论包含 @zhipu，开始处理...")

    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        print(f"✅ 成功连接到 Issue: {issue.title}")
    except Exception as e:
        print(f"❌ 连接 GitHub API 失败: {e}", file=sys.stderr)
        sys.exit(1)

    print("📊 采集 Issue 上下文...")
    recent_comments = get_recent_comments(issue, max_comments=5)

    print("🧠 构建 AI 提示词...")
    prompt = build_context_prompt(
        issue_title=issue.title,
        issue_body=issue.body or "（无正文）",
        trigger_comment=f"@{comment_author}: {comment_body}",
        recent_comments=recent_comments,
    )

    print("🤖 调用智谱 AI 生成计划...")
    ai_response = call_zhipu_api(prompt)

    if not ai_response:
        print("❌ 智谱 AI 未返回有效响应", file=sys.stderr)
        sys.exit(1)

    ai_response = normalize_plan_response(ai_response)
    print("✅ AI 响应生成成功")

    # 验证第一个文件是否存在
    print("🔍 验证计划中的第一个文件...")
    is_valid, error_msg = validate_first_file_exists(ai_response, repo)
    if not is_valid:
        print(f"❌ 计划验证失败: {error_msg}", file=sys.stderr)
        # 在 Issue 中回复错误信息
        issue.create_comment(f"""## ⚠️ Stage 1 计划验证失败

{error_msg}

---

**当前支持的文件类型**：
- ✅ 根目录的 `.md` 文件（如 `README.md`、`CHANGELOG.md`）
- ✅ 一级子目录的 `.md` 文件（如 `docs/CODE_QUALITY.md`、`docs/GUIDE.md`）
- ✅ 根目录的配置文件（仅 `.gitignore`、`.env.example`，append-only 模式）
- ❌ 不支持更深层的目录（如 `docs/deep/file.md`）
- ❌ 不支持其他文件类型（如 `.py`、`requirements.txt`）

**路径规则**：
- 路径按 `/` 分隔后最多 2 段
- 禁止相对路径跳转（如 `../file.md`）

**请重新操作**：
1. 在 Issue 中重新评论 `@zhipu`
2. 确保生成的计划第一个文件符合上述规则

🤖 由 Zhipu AI Stage 1 验证流程生成 | {os.getenv('REPO', '')}""")
        sys.exit(1)

    print("✅ 文件验证通过")

    # 验证 append-only 追加内容的安全性
    print("🔍 验证追加内容安全性...")
    is_safe, safety_error = validate_plan_append_content_safety(ai_response)
    if not is_safe:
        print(f"❌ 追加内容安全验证失败: 检测到疑似真实密钥", file=sys.stderr)
        # 在 Issue 中回复错误信息
        issue.create_comment(safety_error)
        sys.exit(1)

    print("✅ 追加内容安全验证通过")

    try:
        issue.create_comment(ai_response)
        print("✅ 成功评论到 Issue")
    except Exception as e:
        print(f"❌ 评论失败: {e}", file=sys.stderr)
        sys.exit(1)

    print("🎉 任务完成！")


if __name__ == "__main__":
    main()
