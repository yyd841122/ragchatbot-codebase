#!/usr/bin/env python3
"""
Zhipu Issue Agent Executor - Stage 2

当用户在 GitHub Issue 中评论 /zhipu-apply 时触发。
第二阶段：执行型代理

Stage 2 - Step 1 功能：
- 识别 /zhipu-apply 触发
- 读取 Issue 上下文
- 输出 Stage 2 日志
- 回复预备流程评论

后续步骤将逐步实现：
- Step 2: 读取 Issue 和生成计划
- Step 3: 创建分支
- Step 4: 文件修改与 Git 操作
- Step 5: 创建 Draft PR
"""

import os
import sys

# 添加 scripts 目录到 Python 路径，以便导入第一阶段的模块
sys.path.insert(0, '.github/scripts')

from github import Github


def get_env_var(var_name: str) -> str:
    """获取环境变量，如果不存在则退出"""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ 环境变量 {var_name} 未设置", file=sys.stderr)
        sys.exit(1)
    return value


def print_stage2_banner():
    """打印 Stage 2 标识"""
    print("\n" + "="*60)
    print("🚀 Stage 2: 执行型代理 (Execution Agent)")
    print("📋 当前步骤: Step 1 - 预备流程")
    print("="*60 + "\n")


def build_reply_message(issue_title: str, issue_number: int, comment_author: str) -> str:
    """构建预备流程回复消息"""
    return f"""## 🤖 Zhipu Stage 2 执行型代理

**状态**: 已进入执行型代理预备流程 ✅

**当前进度**: Step 1 - 触发链路已打通

---

### 📋 Issue 信息

- **标题**: {issue_title}
- **编号**: #{issue_number}
- **触发者**: @{comment_author}

---

### 🔜 后续步骤

Stage 2 将逐步实现以下功能：

- **Step 2**: 读取 Issue 上下文，生成执行计划
- **Step 3**: 自动创建工作分支
- **Step 4**: 自动修改代码文件
- **Step 5**: 自动创建 Draft PR
- **Step 6**: 完善、错误处理与安全限制

---

### ⚠️ 重要提示

当前为 **Stage 2 - Step 1**，仅验证触发链路。

完整的执行型代理功能将在后续步骤中逐步实现。

---

🤖 由 Zhipu AI Stage 2 预备流程生成 | {os.getenv('REPO', '')}
"""


def main() -> None:
    """主函数"""
    print_stage2_banner()

    print("📍 开始执行 Stage 2 - Step 1 预备流程...\n")

    # 读取环境变量
    print("🔧 读取环境变量...")
    github_token = get_env_var("GITHUB_TOKEN")
    repo_name = get_env_var("REPO")
    issue_number = int(get_env_var("ISSUE_NUMBER"))
    comment_body = get_env_var("COMMENT_BODY")
    comment_author = get_env_var("COMMENT_AUTHOR")

    print(f"  ✅ GITHUB_TOKEN: {'*' * 20}")
    print(f"  ✅ REPO: {repo_name}")
    print(f"  ✅ ISSUE_NUMBER: {issue_number}")
    print(f"  ✅ COMMENT_AUTHOR: {comment_author}")
    print()

    # 连接 GitHub
    print("🔗 连接 GitHub API...")
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        print(f"  ✅ 成功连接到 Issue: #{issue_number} - {issue.title}")
    except Exception as e:
        print(f"  ❌ 连接 GitHub API 失败: {e}", file=sys.stderr)
        sys.exit(1)
    print()

    # 显示触发信息
    print("📝 触发信息:")
    print(f"  📦 Issue 标题: {issue.title}")
    print(f"  💬 Issue 正文: {issue.body[:100] if issue.body else '(无正文)'}...")
    print(f"  🎯 触发命令: {comment_body}")
    print(f"  👤 触发者: @{comment_author}")
    print()

    # 检查是否真的是 /zhipu-apply 触发
    if "/zhipu-apply" not in comment_body:
        print("⚠️ 评论中不包含 /zhipu-apply，跳过处理")
        print("ℹ️ 这可能意味着 workflow 条件配置需要检查")
        return

    print("✅ 确认包含 /zhipu-apply 命令")
    print()

    # 回复预备流程消息
    print("💬 回复预备流程消息到 Issue...")
    try:
        reply_message = build_reply_message(
            issue_title=issue.title,
            issue_number=issue_number,
            comment_author=comment_author
        )
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}", file=sys.stderr)
        sys.exit(1)
    print()

    # 执行 Step 2: 任务分析
    print("="*60)
    print("🔜 进入 Stage 2 - Step 2: 任务分析")
    print("="*60)
    print()
    step2_success = False
    try:
        execute_step2(g, repo, issue, comment_body, comment_author)
        step2_success = True
        print()
        print("="*60)
        print("✅ Stage 2 - Step 2 完成!")
        print("="*60)
    except Exception as e:
        print(f"  ❌ Step 2 执行失败: {e}", file=sys.stderr)
        print(f"  ℹ️ Step 1 已成功完成，仅 Step 2 失败")
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 2 失败，但整体流程继续")
        print("="*60)
    print()

    # 完成
    print("="*60)
    print("✅ Stage 2 全部流程完成!")
    print("="*60)
    print()
    print("📊 本次执行内容:")
    print("  ✅ 识别 /zhipu-apply 触发")
    print("  ✅ 读取 Issue 上下文")
    print("  ✅ 输出 Stage 2 日志")
    print("  ✅ 回复预备流程评论（Step 1）")
    print("  ✅ 查找 Stage 1 计划（Step 2）")
    print("  ✅ 提取任务目标（Step 2）")
    print("  ✅ 回复任务分析评论（Step 2）")
    print()
    print("🔜 下一步: 实现 Step 3 - 创建工作分支")
    print()


def get_existing_plan(issue):
    """查找 Issue 中是否已有 Stage 1 计划

    识别方式：查找 "## 🤖 Zhipu Fix Plan" 标题
    """
    try:
        comments = issue.get_comments()

        # 只检查最近 20 条评论（从新到旧）
        recent_comments = list(comments)[-20:]

        for comment in reversed(recent_comments):
            body = comment.body or ""

            # 查找固定标题
            if "## 🤖 Zhipu Fix Plan" in body:
                return body

        return None

    except Exception as e:
        print(f"  ⚠️ 查找计划出错: {e}")
        return None


def extract_task_objective(issue, existing_plan):
    """提取任务目标

    优先级：
    1. 从 Stage 1 计划的 "问题理解" 提取
    2. 降级：使用 Issue 标题
    """
    if existing_plan:
        # 尝试从 Stage 1 计划提取
        if "### 问题理解" in existing_plan:
            lines = existing_plan.split('\n')
            for i, line in enumerate(lines):
                if "### 问题理解" in line:
                    # 提取接下来 3-5 行
                    objective_lines = []
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('#') and not lines[j].startswith('-'):
                            objective_lines.append(lines[j].strip())
                        elif lines[j].startswith('#'):
                            break
                    if objective_lines:
                        return '\n'.join(objective_lines)

    # 降级：使用 Issue 标题
    title = issue.title if issue.title else "待明确"
    return f"任务目标：{title}"


def build_step2_reply_message(issue_title, task_objective, has_plan, issue_body, existing_plan=None):
    """构建 Step 2 回复消息"""
    repo_name = os.getenv('REPO', '')

    if has_plan:
        # 模式 A：有 Stage 1 计划
        # 尝试提取 Todo List
        steps_text = ""
        if existing_plan and "### Todo List" in existing_plan:
            lines = existing_plan.split('\n')
            in_todo = False
            todo_lines = []
            for line in lines:
                if "### Todo List" in line or "### 计划步骤" in line:
                    in_todo = True
                    continue
                if in_todo and line.strip():
                    if line.startswith('- [ ]') or line.startswith('* '):
                        todo_lines.append(line.strip())
                    elif line.startswith('#') or line.startswith('**'):
                        break
            if todo_lines:
                steps_text = '\n'.join(todo_lines[:5])

        # 尝试提取文件范围
        files_text = ""
        if existing_plan and ("### 计划修改文件" in existing_plan or "计划修改文件" in existing_plan):
            lines = existing_plan.split('\n')
            in_files = False
            file_lines = []
            for line in lines:
                if "### 计划修改文件" in line:
                    in_files = True
                    continue
                if in_files and line.strip():
                    if line.startswith('- `') or line.startswith('* `'):
                        file_lines.append(line.strip())
                    elif line.startswith('#') or line.startswith('**'):
                        break
            if file_lines:
                files_text = '\n'.join(file_lines[:5])

        return f"""## 🤖 Stage 2 任务分析

**状态**: ✅ 已完成分析

**任务目标**: {task_objective}

**执行步骤**:
{steps_text if steps_text else "*将基于 Stage 1 计划执行*"}

**涉及文件**:
{files_text if files_text else "*将基于 Stage 1 计划确定*"}

---

**⚠️ 当前仅做分析，未执行代码修改**

后续版本将逐步实现：创建分支 → 修改代码 → 创建 PR

---
🤖 Zhipu AI Stage 2 | {repo_name}
"""

    else:
        # 模式 B：无 Stage 1 计划（降级模式）
        # 构建上下文摘要
        context_parts = []

        # 添加标题
        if issue_title:
            context_parts.append(f"**Issue 标题**: {issue_title}")

        # 添加正文前 100 字符
        if issue_body and len(issue_body) > 0:
            preview = issue_body[:100] + "..." if len(issue_body) > 100 else issue_body
            context_parts.append(f"**Issue 正文**: {preview}")

        context_text = '\n\n'.join(context_parts) if context_parts else "**Issue 信息**: 标题和正文均为空"

        return f"""## 🤖 Stage 2 任务分析

**状态**: ⚠️ 基础分析完成

**任务目标**: {task_objective}

**Issue 上下文**:
{context_text}

**执行步骤**:
*将基于 Issue 上下文确定*

**涉及文件**:
当前未明确具体文件范围

---

**💡 建议**: 先评论 `@zhipu` 生成详细执行计划，再执行 `/zhipu-apply`

---

**⚠️ 当前仅做分析，未执行代码修改**

后续版本将逐步实现：创建分支 → 修改代码 → 创建 PR

---
🤖 Zhipu AI Stage 2 | {repo_name}
"""


def execute_step2(g, repo, issue, comment_body, comment_author):
    """执行 Step 2 任务分析"""
    print("🔍 查找 Stage 1 计划...")

    # 1. 查找现有计划
    existing_plan = get_existing_plan(issue)
    if existing_plan:
        print("  ✅ 找到 Stage 1 计划")
    else:
        print("  ℹ️ 未找到 Stage 1 计划，将使用基础分析模式")

    # 2. 提取任务目标
    print("🎯 提取任务目标...")
    task_objective = extract_task_objective(issue, existing_plan)
    print(f"  ✅ 任务目标: {task_objective[:50]}...")

    # 3. 生成回复
    print("💬 生成回复消息...")
    reply_message = build_step2_reply_message(
        issue_title=issue.title,
        task_objective=task_objective,
        has_plan=(existing_plan is not None),
        issue_body=issue.body,
        existing_plan=existing_plan
    )

    # 4. 回复到 Issue
    try:
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}")
        raise


if __name__ == "__main__":
    main()
