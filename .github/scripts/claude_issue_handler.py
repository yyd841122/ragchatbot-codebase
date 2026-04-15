#!/usr/bin/env python3
"""
Zhipu AI Issue Handler
Automatically processes GitHub Issues using Zhipu AI to analyze and fix issues.
"""

import os
import sys
import re
import json
import traceback
from github import Github, GithubException
from zhipuai import ZhipuAI

def get_issue_context(repo, issue_number):
    """Get comprehensive issue context"""
    try:
        issue = repo.get_issue(issue_number)

        context = {
            'title': issue.title,
            'body': issue.body,
            'labels': [label.name for label in issue.labels],
            'author': issue.user.login,
            'comments': []
        }

        # Get recent comments
        for comment in issue.get_comments():
            context['comments'].append({
                'author': comment.user.login,
                'body': comment.body,
                'created_at': comment.created_at.isoformat()
            })

        return context
    except GithubException as e:
        print(f"Error fetching issue: {e}")
        return None

def analyze_with_zhipu(context, repo_structure):
    """Analyze issue with Zhipu AI"""
    try:
        api_key = os.environ.get('ZHIPU_API_KEY')
        if not api_key:
            raise ValueError("ZHIPU_API_KEY not found")

        client = ZhipuAI(api_key=api_key)

        # Build the prompt for Zhipu AI
        prompt = f"""你是一个专业的开发者，负责修复 GitHub Issue。

# Issue 详情
标题: {context['title']}
作者: {context['author']}
标签: {', '.join(context['labels'])}

# Issue 描述
{context['body']}

# 最近评论
{chr(10).join([f"{c['author']}: {c['body']}" for c in context['comments']])}

# 仓库结构
{repo_structure}

# 你的任务
分析这个 Issue 并提供：
1. 根本原因分析
2. 解决方案思路
3. 需要修改的文件列表
4. 具体的代码修改建议

请按以下格式回复：

## 分析
[对问题的分析]

## 解决方案
[建议的解决方案]

## 需要修改的文件
[需要修改的文件列表]

## 代码修改
```python
# 每个文件的具体修改
```

## 测试方法
[如何测试修复]
"""

        print(f"Calling Zhipu AI API with model: glm-4-flash")

        response = client.chat.completions.create(
            model="glm-4-flash",  # 使用与项目相同的模型
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=4096,
        )

        print(f"Zhipu AI API call successful")
        result = response.choices[0].message.content
        print(f"Response length: {len(result)} characters")

        return result
    except Exception as e:
        print(f"Error analyzing with Zhipu AI: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_repository_structure():
    """Get basic repository structure"""
    structure = []
    try:
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common build/cache dirs
            dirs[:] = [d for d in dirs if d not in [
                '.git', '__pycache__', 'node_modules', '.venv',
                'venv', 'dist', 'build', '.pytest_cache'
            ]]

            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.md', '.txt')):
                    rel_path = os.path.relpath(os.path.join(root, file), '.')
                    structure.append(rel_path)

        return '\n'.join(structure[:50])  # Limit to first 50 files
    except Exception as e:
        print(f"Error getting repository structure: {e}")
        return "Unable to retrieve repository structure"

def apply_code_changes(code_changes):
    """Apply code changes suggested by Claude"""
    # This is a placeholder - implementing actual code changes requires
    # careful parsing and application of Claude's suggestions
    print("Code changes analysis received (implementation pending)")
    return False

def create_pull_request(repo, issue, analysis_result):
    """Create a pull request with the fix"""
    try:
        branch_name = f"claude-fix-{issue.number}"

        # Create a new branch
        try:
            # Get default branch
            default_branch = repo.default_branch
            repo.get_branch(default_branch)

            # Create new branch (this requires git operations)
            print(f"Would create branch: {branch_name}")
            # Note: Actual branch creation requires git operations

        except GithubException as e:
            print(f"Error creating branch: {e}")
            return False

        # Create pull request
        pr_title = f"[Zhipu AI] 修复 Issue #{issue.number}: {issue.title}"
        pr_body = f"""## Zhipu AI 自动修复

此 Pull Request 由 Zhipu AI 自动生成，用于修复 Issue #{issue.number}。

## 原始 Issue
{issue.title}

## 分析和解决方案
{analysis_result}

## 测试
请在合并前审查和测试这些更改。

---

*此 PR 由 Zhipu AI Issue Handler 创建*
"""

        # Note: Actual PR creation requires commits to be made first
        print(f"Would create PR: {pr_title}")
        print(f"Branch: {branch_name}")
        print(f"Body: {pr_body}")

        return True

    except Exception as e:
        print(f"Error creating pull request: {e}")
        return False

def add_issue_comment(repo, issue_number, message):
    """Add a comment to the issue"""
    try:
        issue = repo.get_issue(issue_number)
        issue.create_comment(message)
        return True
    except GithubException as e:
        print(f"Error adding comment: {e}")
        return False

def main():
    """Main workflow execution"""
    try:
        print("=" * 60)
        print("🤖 Zhipu AI Issue Handler Started")
        print("=" * 60)

        # Debug: Print all environment variables
        print("🔍 Environment Variables Check:")
        for key, value in os.environ.items():
            if 'TOKEN' in key or 'KEY' in key or 'SECRET' in key:
                print(f"  {key}: {'*' * 8}...{value[-4:] if value else 'None'}")
            elif key.startswith('GITHUB_') or key in ['REPO_NAME', 'ISSUE_NUMBER']:
                print(f"  {key}: {value}")

        # Validate critical environment variables
        print("\n🔍 Validating environment variables...")

        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN not found in environment")

        repo_name = os.environ.get('REPO_NAME')
        if not repo_name:
            raise ValueError("REPO_NAME not found in environment")

        issue_number_str = os.environ.get('ISSUE_NUMBER')
        if not issue_number_str:
            raise ValueError("ISSUE_NUMBER not found in environment")

        zhipu_key = os.environ.get('ZHIPU_API_KEY')
        if not zhipu_key:
            raise ValueError("ZHIPU_API_KEY not found in environment")

        print("✅ All environment variables validated")

        try:
            issue_number = int(issue_number_str)
        except ValueError:
            raise ValueError(f"ISSUE_NUMBER must be a number, got: {issue_number_str}")

        print(f"📝 Processing issue #{issue_number} in {repo_name}")
        print("-" * 60)

        # Initialize GitHub client
        print("🔗 Connecting to GitHub...")
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        print(f"✅ Connected to repository: {repo.full_name}")

        # Get issue context
        print(f"📥 Fetching issue #{issue_number}...")
        context = get_issue_context(repo, issue_number)
        if not context:
            raise ValueError("Failed to get issue context")

        print(f"✅ Issue fetched: {context['title']}")
        print(f"   Author: {context['author']}")
        print(f"   Labels: {', '.join(context['labels'])}")

        # Get repository structure
        print("📁 Analyzing repository structure...")
        repo_structure = get_repository_structure()
        print(f"✅ Found {len(repo_structure.split(chr(10)))} files")

        # Analyze with Zhipu AI
        print("🤖 Calling Zhipu AI API...")
        analysis_result = analyze_with_zhipu(context, repo_structure)

        if not analysis_result:
            raise ValueError("Failed to analyze issue with Zhipu AI")

        print("✅ AI analysis completed")

        # Post initial analysis as comment
        print("💬 Posting analysis to issue...")
        comment_message = f"""## 🤖 Zhipu AI 分析

{analysis_result}

---
*由智谱AI自动生成*
"""
        if add_issue_comment(repo, issue_number, comment_message):
            print("✅ Analysis posted to issue")
        else:
            print("⚠️  Failed to post comment, but analysis was completed")

        print("=" * 60)
        print("🎉 Issue processing completed successfully!")
        print("=" * 60)

    except Exception as e:
        print("=" * 60)
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("=" * 60)
        print("📋 Full traceback:")
        traceback.print_exc()
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()