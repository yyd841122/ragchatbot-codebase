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
**第一个文件必须是仓库根目录的真实文件 README.md**
**禁止使用占位路径（如 path/to/README.md、docs/README.md）**
**当前版本仅支持 README.md，不要计划修改其他类型文件**
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
    """验证计划中的第一个文件是否真实存在

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

    # 检查是否为 README.md
    if first_file != "README.md":
        return False, f"当前版本仅支持 `README.md`，但计划中的第一个文件是 `{first_file}`。请在 Issue 中重新评论 `@zhipu`，并确保第一个文件是 `README.md`。"

    # 验证文件是否存在
    try:
        repo.get_contents(first_file)
        return True, ""
    except Exception:
        return False, f"文件 `{first_file}` 在仓库中不存在。请重新在 Issue 中评论 `@zhipu` 生成正确的计划。"


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

**当前 MVP 限制**：
- 仅支持修改根目录的 `README.md`
- 不支持其他文件类型

**请重新操作**：
1. 在 Issue 中重新评论 `@zhipu`
2. 确保生成的计划第一个文件是 `README.md`

🤖 由 Zhipu AI Stage 1 验证流程生成 | {os.getenv('REPO', '')}""")
        sys.exit(1)

    print("✅ 文件验证通过")

    try:
        issue.create_comment(ai_response)
        print("✅ 成功评论到 Issue")
    except Exception as e:
        print(f"❌ 评论失败: {e}", file=sys.stderr)
        sys.exit(1)

    print("🎉 任务完成！")


if __name__ == "__main__":
    main()
