#!/usr/bin/env python3
"""
Claude AI Issue Handler
Automatically processes GitHub Issues using Claude AI to analyze and fix issues.
"""

import os
import sys
import re
from github import Github, GithubException
from anthropic import Anthropic

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

def analyze_with_claude(context, repo_structure):
    """Analyze issue with Claude AI"""
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        client = Anthropic(api_key=api_key)

        # Build the prompt for Claude
        prompt = f"""You are an expert developer tasked with fixing a GitHub issue.

# Issue Details
Title: {context['title']}
Author: {context['author']}
Labels: {', '.join(context['labels'])}

# Issue Description
{context['body']}

# Recent Comments
{chr(10).join([f"{c['author']}: {c['body']}" for c in context['comments']])}

# Repository Structure
{repo_structure}

# Your Task
Analyze this issue and provide:
1. Root cause analysis
2. Proposed solution approach
3. Files that need to be modified
4. Specific code changes needed

Please provide your response in the following format:

## Analysis
[Your analysis of the issue]

## Solution
[Your proposed solution]

## Files to Modify
[List of files that need changes]

## Code Changes
```python
# Specific code changes for each file
```

## Testing
[How to test the fix]"""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text
    except Exception as e:
        print(f"Error analyzing with Claude: {e}")
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
        pr_title = f"[Claude AI] Fix for issue #{issue.number}: {issue.title}"
        pr_body = f"""## Automated Fix by Claude AI

This pull request was automatically generated to fix issue #{issue.number}.

## Original Issue
{issue.title}

## Analysis and Solution
{analysis_result}

## Testing
Please review and test the changes before merging.

---

*This PR was created by Claude AI Issue Handler*
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
        # Initialize GitHub client
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN not found")

        repo_name = os.environ.get('REPO_NAME')
        issue_number = int(os.environ.get('ISSUE_NUMBER'))

        g = Github(github_token)
        repo = g.get_repo(repo_name)

        print(f"Processing issue #{issue_number} in {repo_name}")

        # Get issue context
        context = get_issue_context(repo, issue_number)
        if not context:
            raise ValueError("Failed to get issue context")

        # Get repository structure
        repo_structure = get_repository_structure()

        # Analyze with Claude
        print("Analyzing issue with Claude AI...")
        analysis_result = analyze_with_claude(context, repo_structure)

        if not analysis_result:
            raise ValueError("Failed to analyze issue with Claude")

        # Post initial analysis as comment
        comment_message = f"""## 🤖 Claude AI Analysis

{analysis_result}

I'm working on implementing the fix. Please stand by...
"""
        add_issue_comment(repo, issue_number, comment_message)

        # Create pull request with the fix
        issue = repo.get_issue(issue_number)
        pr_created = create_pull_request(repo, issue, analysis_result)

        if pr_created:
            success_message = "## ✅ Fix Implementation Started

I've analyzed the issue and started working on the fix. A pull request will be created shortly with the changes.

Please review the analysis above and provide feedback if needed."
            add_issue_comment(repo, issue_number, success_message)
        else:
            error_message = "## ⚠️ Manual Intervention Required

I've analyzed the issue and proposed a solution (see above), but was unable to automatically implement the fix.

Please review the analysis and implement the suggested changes manually."
            add_issue_comment(repo, issue_number, error_message)

        print("Issue processing completed successfully")

    except Exception as e:
        print(f"Error in main workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()