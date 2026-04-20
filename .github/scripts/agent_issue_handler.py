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
- `path/to/file1` - [修改目的]
- `path/to/file2` - [修改目的]
- ...

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

    try:
        issue.create_comment(ai_response)
        print("✅ 成功评论到 Issue")
    except Exception as e:
        print(f"❌ 评论失败: {e}", file=sys.stderr)
        sys.exit(1)

    print("🎉 任务完成！")


if __name__ == "__main__":
    main()
