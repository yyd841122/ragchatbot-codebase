import os
import sys
import traceback
from typing import List

from github import Github
from github.PullRequest import PullRequest
from zhipuai import ZhipuAI


MAX_FILES = 10
MAX_PATCH_CHARS_PER_FILE = 3000
MODEL_NAME = "glm-4.5"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_files_summary(pr: PullRequest) -> str:
    """
    Build a readable summary of changed files and partial diffs.
    Limit file count and patch size to avoid overly large prompts.
    """
    summaries: List[str] = []
    files = list(pr.get_files())

    for index, file in enumerate(files[:MAX_FILES], start=1):
        patch = file.patch or ""
        patch = patch[:MAX_PATCH_CHARS_PER_FILE]

        summaries.append(
            f"""### File {index}
Filename: {file.filename}
Status: {file.status}
Additions: {file.additions}
Deletions: {file.deletions}
Changes: {file.changes}

Patch:
{patch if patch else "[No patch available]"}
"""
        )

    if len(files) > MAX_FILES:
        summaries.append(
            f"\n[Only the first {MAX_FILES} changed files are included. Total files changed: {len(files)}]"
        )

    return "\n".join(summaries)


def build_prompt(pr: PullRequest, comment_body: str, files_summary: str) -> str:
    title = pr.title or ""
    body = pr.body or ""

    return f"""
请你扮演一位资深的 Pull Request 审查助手，基于下面的 PR 信息，输出一份结构化的中文分析。

【触发评论】
{comment_body}

【PR 标题】
{title}

【PR 描述】
{body}

【变更文件与部分 diff】
{files_summary}

请按以下结构输出：

## 一、PR 功能总结
用 3-5 条简洁说明这个 PR 在做什么。

## 二、重点风险点
指出可能存在的问题、隐患或需要重点关注的地方。

## 三、建议重点 Review 的内容
说明 reviewer 应该优先检查哪些模块、逻辑或文件。

## 四、建议补充的测试
列出建议增加或重点验证的测试场景。

## 五、总体建议
给出一个总体结论，例如：
- 可以继续 review
- 建议补充测试后再合并
- 建议先修复某些风险点再继续

要求：
1. 全部用简体中文输出
2. 语言清晰、专业、简明
3. 如果信息不足，要明确指出“信息不足”
4. 不要编造仓库中不存在的实现细节
""".strip()


def call_zhipu(prompt: str, api_key: str) -> str:
    client = ZhipuAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的 GitHub Pull Request 代码审查助手，擅长总结、发现风险、给出测试建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def post_comment(pr: PullRequest, content: str, author: str) -> None:
    comment = f"""## 🤖 智谱 PR 分析

触发人：`@{author}`

{content}

---
> 触发方式：在 PR 评论中输入 `/zhipu-review`
"""
    pr.create_issue_comment(comment)


def main() -> None:
    github_token = require_env("GITHUB_TOKEN")
    zhipu_api_key = require_env("ZHIPU_API_KEY")
    repo_name = require_env("REPO")
    pr_number = require_env("PR_NUMBER")
    comment_body = require_env("COMMENT_BODY")
    comment_author = os.getenv("COMMENT_AUTHOR", "unknown")

    print("=== Environment Check ===")
    print(f"GITHUB_TOKEN: {'OK' if github_token else 'MISSING'}")
    print(f"ZHIPU_API_KEY: {'OK' if zhipu_api_key else 'MISSING'}")
    print(f"REPO: {repo_name}")
    print(f"PR_NUMBER: {pr_number}")
    print(f"COMMENT_AUTHOR: {comment_author}")

    gh = Github(github_token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))

    print(f"Loaded PR #{pr.number}: {pr.title}")

    files_summary = build_files_summary(pr)
    prompt = build_prompt(pr, comment_body, files_summary)

    print("Calling Zhipu AI...")
    result = call_zhipu(prompt, zhipu_api_key)

    print("Posting PR comment...")
    post_comment(pr, result, comment_author)

    print("SUCCESS: PR review completed and comment posted")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR:", str(exc))
        traceback.print_exc()
        sys.exit(1)