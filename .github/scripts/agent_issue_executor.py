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
- Step 6: Draft PR 创建
"""

import os
import sys
import base64
import time

# 添加 scripts 目录到 Python 路径，以便导入第一阶段的模块
sys.path.insert(0, '.github/scripts')

from github import Github
from github import UnknownObjectException
import zhipuai


def get_env_var(var_name: str) -> str:
    """获取环境变量，如果不存在则退出"""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ 环境变量 {var_name} 未设置", file=sys.stderr)
        sys.exit(1)
    return value


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


def build_step5_file_not_found_message(file_path: str) -> str:
    """构建文件不存在的错误消息

    Args:
        file_path: 文件路径

    Returns:
        格式化的错误消息
    """
    return f"""## 🤖 Zhipu Stage 2 - Step 5 执行结果

**状态**: ❌ 文件不存在

**目标文件**: `{file_path}`

**原因**: 在仓库中未找到该文件

**如何修复**：
1. 检查文件路径是否正确
2. 确认文件已在仓库中存在
3. 在 Issue 中重新评论 `@zhipu`，生成修正后的计划

---

🤖 由 Zhipu AI Stage 2 - Step 5 生成
"""


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

    # 初始化 Steps 1-5 整体状态
    all_steps_success = True

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
        all_steps_success = False
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 2 失败，但整体流程继续")
        print("="*60)
    print()

    # 执行 Step 3: 创建工作分支
    print("="*60)
    print("🔜 进入 Stage 2 - Step 3: 创建工作分支")
    print("="*60)
    print()

    # 生成工作分支名称（供 Step 6 使用）
    branch_name = generate_branch_name(issue_number)
    print(f"  📌 工作分支名称: {branch_name}")
    print()

    step3_success = False
    try:
        execute_step3(g, repo, issue, issue_number)
        step3_success = True
        print()
        print("="*60)
        print("✅ Stage 2 - Step 3 完成!")
        print("="*60)
    except Exception as e:
        print(f"  ❌ Step 3 执行失败: {e}", file=sys.stderr)
        print(f"  ℹ️ Step 1 和 Step 2 已成功完成，仅 Step 3 失败")
        all_steps_success = False
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 3 失败，但整体流程继续")
        print("="*60)
    print()

    # 执行 Step 4: 代码修改预览
    print("="*60)
    print("🔜 进入 Stage 2 - Step 4: 代码修改预览")
    print("="*60)
    print()
    step4_success = False
    try:
        execute_step4(g, repo, issue, issue_number)
        step4_success = True
        print()
        print("="*60)
        print("✅ Stage 2 - Step 4 完成!")
        print("="*60)
    except Exception as e:
        print(f"  ❌ Step 4 执行失败: {e}", file=sys.stderr)
        print(f"  ℹ️ Step 1/2/3 已成功完成，仅 Step 4 失败")
        all_steps_success = False
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 4 失败，但整体流程继续")
        print("="*60)
    print()

    # 执行 Step 5: 文件修改并提交
    print("="*60)
    print("🔜 进入 Stage 2 - Step 5: 文件修改并提交")
    print("="*60)
    print()
    step5_success = False
    step5_result = None
    try:
        if step4_success:  # 仅在 Step 4 成功后执行
            step5_result = execute_step5(g, repo, issue, issue_number)

            # 根据返回结果判断状态
            if step5_result['status'] == 'success':
                step5_success = True
                print()
                print("="*60)
                print("✅ Stage 2 - Step 5 完成!")
                print("="*60)
            elif step5_result['status'] == 'skipped':
                all_steps_success = False
                print()
                print("="*60)
                print(f"⚠️ Stage 2 - Step 5 跳过: {step5_result['reason']}")
                print("="*60)
            else:  # failed
                all_steps_success = False
                print()
                print("="*60)
                print(f"❌ Stage 2 - Step 5 失败: {step5_result['reason']}")
                print("="*60)
        else:
            print("  ℹ️ Step 4 失败，跳过 Step 5")
            print()
            print("="*60)
            print("⚠️ Stage 2 - Step 5 跳过")
            print("="*60)
    except Exception as e:
        print(f"  ❌ Step 5 执行失败: {e}", file=sys.stderr)
        print(f"  ℹ️ Step 1/2/3/4 已成功完成，仅 Step 5 失败")
        all_steps_success = False
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 5 失败，但整体流程继续")
        print("="*60)
    print()

    # 执行 Step 6: 创建 Draft PR
    print("="*60)
    print("🔜 进入 Stage 2 - Step 6: 创建 Draft PR")
    print("="*60)
    print()
    step6_success = False
    step6_start_time = time.time()

    try:
        # 仅在 Step 5 成功时执行 Step 6
        if step5_success:
            # 获取 Stage 1 计划（复用 Step 2 的逻辑）
            stage1_plan_for_step6 = get_existing_plan(issue)

            step6_result = execute_step6(
                g=g,
                repo=repo,
                issue=issue,
                issue_number=issue_number,
                branch_name=branch_name,
                stage1_plan=stage1_plan_for_step6,
                step5_result=step5_result
            )

            step6_duration = time.time() - step6_start_time

            if step6_result['status'] == 'success':
                step6_success = True
                print()
                print("="*60)
                print("✅ Stage 2 - Step 6 完成!")
                print("="*60)
            elif step6_result['status'] == 'skipped':
                print()
                print("="*60)
                print(f"⚠️ Stage 2 - Step 6 跳过: {step6_result['reason']}")
                print("="*60)
            else:  # failed
                print()
                print("="*60)
                print(f"❌ Stage 2 - Step 6 失败: {step6_result['reason']}")
                print("="*60)
        else:
            print("  ℹ️ Step 5 未成功，跳过 Step 6")
            print()
            print("="*60)
            print("⏭️ Stage 2 - Step 6 跳过")
            print("="*60)
            step6_duration = time.time() - step6_start_time

    except Exception as e:
        step6_duration = time.time() - step6_start_time
        print(f"  ❌ Step 6 执行失败: {e}", file=sys.stderr)
        print(f"  ℹ️ Step 1/2/3/4/5 已成功完成，仅 Step 6 失败")
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 6 失败，但整体流程继续")
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
    print("  ✅ 创建工作分支（Step 3）")
    print("  ✅ 回复分支创建结果（Step 3）")
    print("  ✅ 读取第一个目标文件（Step 4）")
    print("  ✅ 生成修改预览（Step 4）")
    print("  ✅ 回复预览结果（Step 4）")
    if step5_success:
        print("  ✅ 修改文件并创建 commit（Step 5）")
        print("  ✅ 回复修改结果（Step 5）")
    else:
        print("  ⚠️ Step 5 未执行或失败")
    if step6_success:
        print("  ✅ 创建 Draft PR（Step 6）")
        print("  ✅ 回复 PR 创建结果（Step 6）")
    elif step5_success:
        print("  ⚠️ Step 6 未执行或失败")
    print()

    # 最终状态总结
    print("="*60)
    print("📊 最终状态总结")
    print("="*60)
    print(f"Steps 1-5 整体状态: {'✅ 全部成功' if all_steps_success else '⚠️ 存在失败步骤'}")
    print(f"Step 6 状态: {'✅ 成功' if step6_success else '⚠️ 未成功/未执行'}")
    print("="*60)
    print()
    print("🔜 后续步骤将在下一阶段实现")
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


def generate_branch_name(issue_number: int) -> str:
    """生成工作分支名称

    命名规则: zhipu/issue-{issue_number}
    """
    return f"zhipu/issue-{issue_number}"


def get_default_branch(repo) -> str:
    """获取仓库默认分支名称"""
    try:
        default_branch = repo.default_branch
        if not default_branch:
            raise ValueError("default_branch is None")
        return default_branch
    except Exception as e:
        print(f"  ❌ 获取默认分支失败: {e}")
        raise


def branch_exists(repo, branch_name: str) -> bool:
    """检查分支是否存在

    Returns:
        bool: True if branch exists, False otherwise

    Raises:
        Exception: 其他异常（权限不足、API错误、网络错误等）会继续抛出
    """
    try:
        repo.get_branch(branch_name)
        return True
    except UnknownObjectException:
        # 分支不存在（404）
        return False
    # 其他异常（403、API错误、网络错误等）继续抛出


def create_branch(repo, branch_name: str, base_branch: str) -> bool:
    """创建新分支

    Args:
        repo: Github repository object
        branch_name: 新分支名称
        base_branch: 基础分支名称

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # 获取基础分支的最新 commit SHA
        base_branch_ref = repo.get_branch(base_branch)
        commit_sha = base_branch_ref.commit.sha

        # 创建新分支引用
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=commit_sha
        )
        return True
    except Exception as e:
        print(f"  ❌ 创建分支失败: {e}")
        raise


def build_step3_reply_message(issue_number: int, branch_name: str, base_branch: str, status: str, error_msg: str = None) -> str:
    """构建 Step 3 回复消息

    Args:
        issue_number: Issue 编号
        branch_name: 分支名称
        base_branch: 基础分支名称
        status: 状态 ('created', 'already_exists', 'failed')
        error_msg: 错误信息（仅 status='failed' 时使用）

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    if status == 'created':
        return f"""## 🤖 Stage 3 工作分支创建

**状态**: ✅ 分支已创建

**Issue 编号**: #{issue_number}

**分支名称**: `{branch_name}`

**基于**: `{base_branch}` 分支

---

**⚠️ 当前未执行代码修改**

---
🤖 Zhipu AI Stage 3 | {repo_name}
"""

    elif status == 'already_exists':
        return f"""## 🤖 Stage 3 工作分支检查

**状态**: ℹ️ 工作分支已存在

**Issue 编号**: #{issue_number}

**分支名称**: `{branch_name}`

**说明**: 将复用现有分支，无需重复创建

---

**⚠️ 当前未执行代码修改**

---
🤖 Zhipu AI Stage 3 | {repo_name}
"""

    else:  # status == 'failed'
        return f"""## 🤖 Stage 3 工作分支创建

**状态**: ❌ 分支创建失败

**失败原因**: {error_msg or "未知错误"}

---

**ℹ️ Step 1 和 Step 2 已成功完成**

---
🤖 Zhipu AI Stage 3 | {repo_name}
"""


def execute_step3(g, repo, issue, issue_number: int):
    """执行 Step 3 创建工作分支"""
    print("🔍 准备创建工作分支...")

    # 1. 获取默认分支
    print("📌 获取仓库默认分支...")
    try:
        base_branch = get_default_branch(repo)
        print(f"  ✅ 默认分支: {base_branch}")
    except Exception as e:
        print(f"  ❌ 获取默认分支失败")
        raise

    # 2. 生成分支名称
    print("🏷️  生成分支名称...")
    branch_name = generate_branch_name(issue_number)
    print(f"  ✅ 分支名称: {branch_name}")

    # 3. 检查分支是否已存在
    print("🔍 检查分支是否已存在...")
    if branch_exists(repo, branch_name):
        print("  ℹ️ 分支已存在，跳过创建")
        status = 'already_exists'

        # 生成回复
        reply_message = build_step3_reply_message(
            issue_number=issue_number,
            branch_name=branch_name,
            base_branch=base_branch,
            status=status
        )
    else:
        print("  ℹ️ 分支不存在，准备创建...")
        status = 'created'

        try:
            # 创建分支
            create_branch(repo, branch_name, base_branch)
            print("  ✅ 分支创建成功")
        except Exception as e:
            print(f"  ❌ 分支创建失败")
            status = 'failed'
            raise

        # 生成回复
        reply_message = build_step3_reply_message(
            issue_number=issue_number,
            branch_name=branch_name,
            base_branch=base_branch,
            status=status
        )

    # 4. 回复到 Issue
    print("💬 回复消息到 Issue...")
    try:
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}")
        raise

    print(f"  ✅ Step 3 完成，状态: {status}")


def extract_first_file_path(existing_plan: str) -> str:
    """从 Stage 1 计划中提取第一个文件路径

    Args:
        existing_plan: Stage 1 计划的完整内容

    Returns:
        str: 第一个文件路径，如果未找到则返回空字符串
    """
    if not existing_plan:
        return ""

    # 查找"计划修改文件"章节
    lines = existing_plan.split('\n')
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
            # 格式1: Markdown 列表: - `backend/app.py`
            # 格式2: 仅反引号: `backend/app.py`
            # 格式3: 普通文本: backend/app.py

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
                # 简单的启发式检查：看起来像文件路径（包含斜杠或点）
                if '/' in cleaned_line or '.' in cleaned_line:
                    return cleaned_line

    return ""


def read_file_content_safe(repo, file_path: str, branch_name: str) -> dict:
    """安全读取指定分支的文件内容

    Args:
        repo: Github repository object
        file_path: 文件路径
        branch_name: 分支名称

    Returns:
        dict: {
            'success': bool,
            'content': str (base64 解码后的内容),
            'size': int (文件大小，字节数),
            'error': str (错误信息，仅在失败时)
        }
    """
    try:
        # 获取文件内容
        content_file = repo.get_contents(file_path, ref=branch_name)

        # 检查是否为文件（而不是目录）
        if content_file.type == 'dir':
            return {
                'success': False,
                'content': '',
                'size': 0,
                'error': f"路径 `{file_path}` 是目录而非文件"
            }

        # 解码内容
        decoded_content = base64.b64decode(content_file.content).decode('utf-8')

        return {
            'success': True,
            'content': decoded_content,
            'size': content_file.size or len(decoded_content),
            'error': None
        }

    except UnknownObjectException:
        return {
            'success': False,
            'content': '',
            'size': 0,
            'error': f"文件 `{file_path}` 在分支 `{branch_name}` 上不存在"
        }
    except Exception as e:
        return {
            'success': False,
            'content': '',
            'size': 0,
            'error': f"读取文件失败: {str(e)}"
        }


def build_step4_reply_message(
    issue_number: int,
    branch_name: str,
    file_path: str,
    file_size: int,
    content_preview: str,
    has_multiple_files: bool = False
) -> str:
    """构建 Step 4 预览成功时的回复消息

    Args:
        issue_number: Issue 编号
        branch_name: 工作分支名称
        file_path: 文件路径
        file_size: 文件大小（字节数）
        content_preview: 内容摘要（前 80 个字符）
        has_multiple_files: 是否存在多个文件（True 时添加提示）

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    # 构建多文件提示
    multiple_files_hint = ""
    if has_multiple_files:
        multiple_files_hint = "\n\n**⚠️ 当前 MVP 版本仅预览第一个文件，其余文件后续扩展**"

    return f"""## 🤖 Stage 4 代码修改预览

**状态**: ✅ 预览已生成

**工作分支**: `{branch_name}`

**预览文件**: `{file_path}`

**文件大小**: {file_size} bytes

**内容摘要**:
```
{content_preview}
```{multiple_files_hint}

---

**⚠️ 当前仅是预览，尚未真正写入仓库**

---
🤖 Zhipu AI Stage 4 | {repo_name}
"""


def build_step4_failure_message(file_path: str, error_msg: str) -> str:
    """构建 Step 4 文件读取失败时的回复消息

    Args:
        file_path: 尝试读取的文件路径
        error_msg: 错误信息

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 4 代码修改预览

**状态**: ❌ 文件读取失败

**尝试读取的文件**: `{file_path}`

**失败原因**: {error_msg}

---

### ⚠️ 当前 MVP 限制

- **仅支持修改根目录的 `README.md`**
- **不支持相对路径**（如 `path/to/README.md`、`docs/README.md`）
- **不支持其他文件类型**（如 `.py`、`.yml`、`.json`）

### 💡 可能的原因

1. Stage 1 计划中的文件路径不正确
2. Stage 1 计划包含占位路径
3. Stage 1 文件校验未生效（bug）

### 🔧 解决方法

请在 Issue 中重新评论 `@zhipu`，确保：
- 第一个文件是 `README.md`
- 不使用占位路径或相对路径

如持续失败，请联系开发者检查 Stage 1 文件校验逻辑。

---

**ℹ️ Step 1/2/3 已成功完成**

---
🤖 Zhipu AI Stage 4 | {repo_name}
"""


def build_step4_no_file_message() -> str:
    """构建 Step 4 未识别到文件时的回复消息

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 4 代码修改预览

**状态**: ⚠️ 未识别到修改文件

**问题**: 从 Stage 1 计划中未找到"计划修改文件"章节或章节下无文件列表

**建议**:
- 先评论 `@zhipu` 生成详细执行计划
- 或在 Issue 中明确指定要修改的文件路径

---

**ℹ️ Step 1/2/3 已成功完成**

---
🤖 Zhipu AI Stage 4 | {repo_name}
"""


def execute_step4(g, repo, issue, issue_number: int):
    """执行 Step 4 代码修改预览"""
    print("🔍 准备执行代码修改预览...")

    # 1. 生成工作分支名称（复用 Step 3 的逻辑）
    branch_name = generate_branch_name(issue_number)
    print(f"  📌 工作分支: {branch_name}")

    # 2. 获取 Stage 1 计划（复用 Step 2 的逻辑）
    print("🔍 查找 Stage 1 计划...")
    existing_plan = get_existing_plan(issue)

    if not existing_plan:
        print("  ℹ️ 未找到 Stage 1 计划")
        # 回复：未识别到文件
        reply_message = build_step4_no_file_message()
        issue.create_comment(reply_message)
        print("  ✅ 已回复未识别到文件消息")
        return

    print("  ✅ 找到 Stage 1 计划")

    # 3. 提取第一个文件路径
    print("🔍 提取第一个文件路径...")
    file_path = extract_first_file_path(existing_plan)

    if not file_path:
        print("  ℹ️ 未识别到文件路径")
        # 回复：未识别到文件
        reply_message = build_step4_no_file_message()
        issue.create_comment(reply_message)
        print("  ✅ 已回复未识别到文件消息")
        return

    print(f"  ✅ 文件路径: {file_path}")

    # 4. 检查是否存在多个文件
    has_multiple_files = False
    lines = existing_plan.split('\n')
    in_target_section = False
    file_count = 0
    for line in lines:
        if "### 计划修改文件" in line:
            in_target_section = True
            continue
        if in_target_section:
            if not line.strip():
                continue
            if line.strip().startswith('###'):
                break
            # 简单计数：包含反引号或斜杠的行
            if '`' in line or '/' in line:
                file_count += 1

    if file_count > 1:
        has_multiple_files = True
        print(f"  ℹ️ 检测到 {file_count} 个文件，当前仅预览第一个")

    # 5. 读取文件内容
    print(f"📖 读取文件内容（分支: {branch_name}）...")
    result = read_file_content_safe(repo, file_path, branch_name)

    if not result['success']:
        print(f"  ❌ 读取失败: {result['error']}")
        # 回复：文件读取失败
        reply_message = build_step4_failure_message(file_path, result['error'])
        issue.create_comment(reply_message)
        print("  ✅ 已回复文件读取失败消息")
        return

    print(f"  ✅ 读取成功，文件大小: {result['size']} bytes")

    # 6. 生成内容摘要（固定 80 个字符）
    content_preview = result['content'][:80]
    if len(result['content']) > 80:
        content_preview += "..."

    print(f"  📝 内容摘要: {content_preview[:50]}...")

    # 7. 生成回复
    print("💬 生成回复消息...")
    reply_message = build_step4_reply_message(
        issue_number=issue_number,
        branch_name=branch_name,
        file_path=file_path,
        file_size=result['size'],
        content_preview=content_preview,
        has_multiple_files=has_multiple_files
    )

    # 8. 回复到 Issue
    try:
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}")
        raise

    print(f"  ✅ Step 4 完成")


def construct_modification_objective(file_path: str, issue_title: str) -> str:
    """构造简洁明确的修改目标

    使用保守的规则化方式，基于文件路径和 Issue 标题构造修改目标。
    当前版本优先保证 README 测试场景稳定，不追求泛化。

    注意：
        - Issue 标题不直接作为 AI Prompt 原文输入
        - Issue 标题用于代码中的规则化目标构造
        - "只在末尾追加"规则主要用于 README 的第二轮验证样本
        - 后续扩展到其他 Markdown 文件时再评估是否放宽

    Args:
        file_path: 文件路径（如 "README.md" 或 "docs/GUIDE.md"）
        issue_title: Issue 标题（用于规则化判断，不直接传递给 AI）

    Returns:
        str: 简洁明确的修改目标描述
    """
    # 统一路径格式
    file_path_normalized = file_path.replace('\\', '/').lower()
    issue_title_normalized = (issue_title or "").lower()

    # 提取是否为 README
    is_readme = file_path_normalized == "readme.md" or file_path_normalized.endswith("/readme.md")

    # 提取 basename（用于配置文件判断）
    basename = file_path_normalized.split('/')[-1]

    # 配置文件 append-only 模式
    if basename == '.gitignore':
        return "在 .gitignore 文件末尾追加新的忽略规则，保持原有规则不变。只返回要追加的内容，不要返回完整的 .gitignore 文件。"
    if basename == '.env.example':
        return "在 .env.example 文件末尾追加新的环境变量示例，保持原有变量不变。只返回要追加的内容，不要返回完整的 .env.example 文件。"

    # 规则 1：README.md 测试场景（保守固定模板）
    if is_readme and ("测试" in issue_title_normalized or "test" in issue_title_normalized):
        return "在 README.md 末尾追加一个简单测试章节，保持原有结构不变。"

    # 规则 2：其他 README.md 场景
    if is_readme:
        return "在 README.md 末尾追加简单内容，保持原有结构不变。"

    # 规则 3：其他 Markdown 文件
    if file_path_normalized.endswith('.md'):
        return f"在 {file_path} 中进行相关修改，保持原有结构不变。"

    # 默认
    return "对文档进行小范围修改，保持原有结构不变。"


def generate_modified_content(
    current_content: str,
    modification_objective: str,
    file_path: str
) -> str:
    """调用 Zhipu AI 生成修改后的文件内容

    Args:
        current_content: 当前文件内容
        modification_objective: 修改目标（简洁明确，由 construct_modification_objective 构造）
        file_path: 文件路径

    Returns:
        str: AI 生成的修改后内容，如果失败则返回空字符串
             对于配置文件，返回要追加的内容片段（不包含原有内容）
             对于 Markdown 文件，返回完整的文件内容
    """
    try:
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            print("  ❌ ZHIPU_API_KEY 未设置")
            return ""

        client = zhipuai.ZhipuAI(api_key=api_key)

        # 判断是否为 append-only 配置文件
        file_path_normalized = file_path.replace('\\', '/').lower()
        basename = file_path_normalized.split('/')[-1]
        is_append_only_config = basename in ['.gitignore', '.env.example']

        # 对于 append-only 配置文件，使用特殊的 Prompt
        if is_append_only_config:
            prompt = f"""你是一个配置文件修改助手。

## 任务
{modification_objective}

## 配置文件路径
{file_path}

## 当前配置文件末尾内容（最后 10 行）
```
{_get_last_n_lines(current_content, 10)}
```

---

**修改要求（必须严格遵守）**：

**1. 只生成要追加的内容**：
- ✅ 只返回要追加到文件末尾的新内容
- ❌ 不要返回完整的配置文件
- ❌ 不要包含原有内容

**2. 禁止写入的内容（严格禁止）**：
- ❌ 不要写入真实的 API 密钥、密码、敏感信息
- ❌ 不要写入 "示例密钥"、"your-api-key-here" 等占位符
- ❌ 不要写入 Issue 标题、Issue 编号

**3. 内容格式要求**：
- **.gitignore**: 每行一个忽略规则，格式如 `*.log` 或 `temp/`
- **.env.example**: 每行一个环境变量示例，格式如 `VAR_NAME=example_value` 或 `# 注释`

**输出要求**：
1. 只返回要追加的内容片段
2. 不要包含解释
3. 不要包含 markdown 代码块标记（\\`\\`\\`）
4. 第一行前面不要加换行符
5. 最后一行后面加一个换行符
"""
        else:
            # Markdown 文件使用原有的 Prompt
            prompt = f"""你是一个文档修改助手。

## 任务
{modification_objective}

## 当前文件路径
{file_path}

## 当前文件内容
```
{current_content}
```

---

**修改要求（必须严格遵守）**：

**1. 只做必要的修改**：
- 优先追求最小范围的局部修改
- 只修改与任务直接相关的内容
- 不要修改无关章节

**2. 禁止写入的内容（严格禁止）**：
- ❌ 不要写入 Issue 标题或正文
- ❌ 不要写入"测试目标"、"测试内容"
- ❌ 不要写入"执行计划"、"Todo List"、"风险提示"、"下一步"
- ❌ 不要写入 Issue 编号（如 Issue #123）
- ❌ 不要写入"Zhipu Fix Plan"或"由 Zhipu AI 生成"

**3. 保持原有结构**：
- ✅ 保持文档的原有结构
- ✅ 保持标题层级
- ✅ 保持格式不变

**输出要求**：
1. 只返回修改后的完整文档内容
2. 不要包含解释
3. 不要包含 markdown 代码块标记（\\`\\`\\`）
4. 直接返回可用的文档内容
"""

        print("  🤖 调用 Zhipu AI 生成修改内容...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            if content:
                # 清理可能的 markdown 代码块标记
                content = content.strip()
                if content.startswith("```"):
                    # 移除第一行的 ```markdown 或 ```
                    lines = content.split('\n')
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    # 移除最后一行的 ```
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = '\n'.join(lines)
                print("  ✅ AI 生成内容成功")
                return content.strip()

        print("  ❌ Zhipu AI 返回了空响应")
        return ""

    except Exception as e:
        print(f"  ❌ 调用 Zhipu AI 失败: {e}")
        return ""


def _get_last_n_lines(content: str, n: int) -> str:
    """获取文本的最后 n 行

    Args:
        content: 文本内容
        n: 行数

    Returns:
        最后 n 行的内容
    """
    lines = content.split('\n')
    if len(lines) <= n:
        return content
    return '\n'.join(lines[-n:])


def validate_append_content(
    file_path: str,
    append_text: str,
    existing_content: str
) -> dict:
    """验证 AI 生成的追加内容是否安全

    检查规则：
    1. 追加内容不能为空
    2. 追加内容不能包含敏感信息（真实密钥、密码等）
    3. 追加内容格式必须正确（.gitignore 或 .env.example）
    4. 追加内容不能重复现有内容（简单检查）

    Args:
        file_path: 文件路径
        append_text: AI 生成的追加内容
        existing_content: 文件现有内容

    Returns:
        dict: {
            'valid': bool,
            'reason': str (如果不合法，说明原因)
        }
    """
    # 统一路径格式
    file_path_normalized = file_path.replace('\\', '/').lower()
    basename = file_path_normalized.split('/')[-1]

    # 检查 1：追加内容不能为空
    if not append_text or not append_text.strip():
        return {
            'valid': False,
            'reason': '追加内容为空'
        }

    # 检查 2：追加内容不能包含敏感信息
    # 对于 .gitignore 和 .env.example 使用不同的检测策略

    if basename == '.gitignore':
        # .gitignore：严格检测，不应该包含任何敏感关键词
        sensitive_patterns = [
            'sk-',            # OpenAI API key
            'api_key',        # 通用 API key
            'secret',         # 密钥
            'password',       # 密码
            'token',          # 令牌
            'AKID',           # AWS Access Key ID
            'wjalr_uxto',     # AWS Secret Access Key pattern
        ]

        append_text_lower = append_text.lower()
        for pattern in sensitive_patterns:
            if pattern.lower() in append_text_lower:
                return {
                    'valid': False,
                    'reason': f'追加内容包含敏感信息（检测到关键词: {pattern}）'
                }

    elif basename == '.env.example':
        # .env.example：检测变量值是否是真实密钥，而不是变量名
        # 允许变量名包含敏感词（如 API_KEY=、SECRET_KEY=）
        # 但检测变量值是否是真实密钥

        lines = append_text.strip().split('\n')
        for line in lines:
            line_stripped = line.strip()

            # 跳过空行和注释
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # 解析环境变量行（格式：VAR_NAME=value 或 VAR_NAME=value # comment）
            if '=' not in line_stripped:
                continue

            # 分割变量名和值
            parts = line_stripped.split('=', 1)
            if len(parts) != 2:
                continue

            var_name = parts[0].strip()
            var_value = parts[1].strip()

            # 检查变量名格式：必须以大写字母开头，只包含大写字母、数字、下划线
            if not var_name:
                return {
                    'valid': False,
                    'reason': '.env.example 文件格式错误：变量名为空'
                }

            if not var_name[0].isupper():
                return {
                    'valid': False,
                    'reason': '.env.example 文件格式错误：变量名必须以大写字母开头'
                }

            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
            if not all(c in valid_chars for c in var_name):
                return {
                    'valid': False,
                    'reason': '.env.example 文件格式错误：变量名包含非法字符（只允许大写字母、数字、下划线）'
                }

            # 移除行尾注释
            if '#' in var_value:
                var_value = var_value.split('#')[0].strip()

            # 检测变量值是否是真实密钥
            # 检测明显的真实密钥模式
            dangerous_patterns = [
                ('sk-', 'OpenAI API key'),
                ('ghp_', 'GitHub personal access token'),
                ('github_pat_', 'GitHub personal access token (fine-grained)'),
                ('wjalr_uxto', 'AWS secret key pattern'),
                ('AKID', 'AWS Access Key ID'),
                ('AIza', 'Google API key'),
            ]

            var_value_lower = var_value.lower()
            for pattern, desc in dangerous_patterns:
                if pattern.lower() in var_value_lower:
                    return {
                        'valid': False,
                        'reason': f'变量值包含疑似真实密钥（检测到 {desc} 模式）'
                    }

            # 检测长随机字符串（可能是真实密钥）
            # 规则：超过 32 个字符，且包含大小写字母、数字、特殊字符
            if len(var_value) > 32:
                # 简单启发式：如果看起来像密钥（高熵值）
                # 包含大写字母、小写字母、数字、特殊字符中的至少 3 种
                has_upper = any(c.isupper() for c in var_value)
                has_lower = any(c.islower() for c in var_value)
                has_digit = any(c.isdigit() for c in var_value)
                has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in var_value)

                complexity = sum([has_upper, has_lower, has_digit, has_special])

                # 如果复杂度高且长度长，可能是真实密钥
                if complexity >= 3 and not any(x in var_value.lower() for x in ['example', 'test', 'your_', 'dummy', 'placeholder', 'xxx']):
                    return {
                        'valid': False,
                        'reason': '变量值看起来像是真实密钥（长随机字符串），请使用示例值'
                    }

            # 检测明显的占位符（这些是允许的）
            allowed_placeholders = [
                'example',
                'test',
                'your_',
                'dummy',
                'placeholder',
                'xxx',
                'replace',
                'changeme',
                '<',
                '>',
            ]

            # 如果变量值包含明显的占位符，则允许
            if any(placeholder in var_value.lower() for placeholder in allowed_placeholders):
                continue

            # 对于非占位符的长值，给出警告但不拒绝（仅记录）
            if len(var_value) > 20:
                # 可能有风险，但不拒绝，让人工 review 决定
                print(f"  ⚠️ 注意：变量 {var_name} 的值较长（{len(var_value)} 字符），请人工 review 确认")

    # 检查 3：追加内容格式必须正确
    if basename == '.gitignore':
        # .gitignore 格式检查
        lines = append_text.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 跳过空行和注释
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # 检查：是否看起来像环境变量格式
            # 如果行包含 "=" 且两边都是简单的字母数字下划线，可能是环境变量
            if '=' in line_stripped and not line_stripped.startswith('#'):
                parts = line_stripped.split('=', 1)
                if len(parts) == 2:
                    left_part = parts[0].strip()
                    right_part = parts[1].strip()

                    # 检查左边是否是纯变量名格式
                    if left_part.replace('_', '').replace('-', '').isalnum():
                        # 检查右边是否也只包含简单字符（没有 .gitignore 常见的通配符）
                        # .gitignore 通常包含 * ? / 等特殊字符
                        ignore_special_chars = set('*?[]/\\')
                        has_ignore_special = any(c in right_part for c in ignore_special_chars)

                        # 如果没有 .gitignore 特殊字符，可能是环境变量
                        if not has_ignore_special and right_part.replace('_', '').replace('-', '.').isalnum():
                            return {
                                'valid': False,
                                'reason': f'.gitignore 文件格式错误：第 {line_num} 行看起来像是环境变量格式（包含 "="），.gitignore 应该只包含忽略规则'
                            }

    elif basename == '.env.example':
        # .env.example 格式检查
        # 注意：变量名格式检查已经在敏感信息检测部分完成
        # 这里只检查是否包含 "="
        lines = append_text.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 跳过空行和注释
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # 检查：非空非注释行应该包含 "="（环境变量格式）
            if '=' not in line_stripped:
                return {
                    'valid': False,
                    'reason': f'.env.example 文件格式错误：第 {line_num} 行不包含 "="，环境变量应该使用 VAR_NAME=value 格式'
                }

    # 检查 4：追加内容不能重复现有内容（精确行级检查）
    # 对于 .gitignore，检查追加的规则是否已经存在
    if basename == '.gitignore':
        # 将现有内容和追加内容都拆分为行，检查重复
        existing_lines = set(line.strip() for line in existing_content.split('\n') if line.strip())
        append_lines = [line.strip() for line in append_text.split('\n') if line.strip()]

        for append_line in append_lines:
            # 跳过注释行
            if append_line.startswith('#'):
                continue

            if append_line in existing_lines:
                return {
                    'valid': False,
                    'reason': f'追加内容与现有内容重复（规则: {append_line}）'
                }
    else:
        # 对于其他文件，使用简单的尾部检查（原有逻辑）
        if len(existing_content) > 50 and len(append_text) > 50:
            existing_tail = existing_content[-50:]
            append_head = append_text[:50]
            if append_head in existing_tail:
                return {
                    'valid': False,
                    'reason': '追加内容可能与现有内容重复'
                }

    # 检查 5：追加内容不能过长（防止 AI 失控）
    append_lines = append_text.split('\n')
    if len(append_lines) > 100:
        return {
            'valid': False,
            'reason': f'追加内容过长（{len(append_lines)} 行，超过 100 行限制）'
        }

    # 检查 6：追加内容单行不能过长
    for line in append_lines:
        if len(line) > 1000:
            return {
                'valid': False,
                'reason': f'追加内容包含过长的行（{len(line)} 字符，超过 1000 字符限制）'
            }

    return {
        'valid': True,
        'reason': None
    }


def append_to_file_content(existing_content: str, append_text: str) -> str:
    """安全地将内容追加到文件末尾

    处理逻辑：
    1. 如果现有内容为空，直接返回追加内容
    2. 如果现有内容最后一行没有换行符，先添加一个
    3. 追加新内容
    4. 确保最终内容以换行符结尾

    Args:
        existing_content: 文件现有内容
        append_text: 要追加的内容

    Returns:
        str: 追加后的完整内容
    """
    # 如果现有内容为空，直接返回追加内容
    if not existing_content or not existing_content.strip():
        return append_text.rstrip('\n') + '\n'

    # 确保现有内容以换行符结尾
    if not existing_content.endswith('\n'):
        existing_content = existing_content + '\n'

    # 追加新内容
    result = existing_content + append_text

    # 确保最终内容以换行符结尾
    if not result.endswith('\n'):
        result = result + '\n'

    return result


def validate_generated_content(
    new_content: str,
    original_content: str
) -> dict:
    """验证 AI 生成内容的合法性

    Args:
        new_content: AI 生成的新内容
        original_content: 原始文件内容

    Returns:
        dict: {
            'valid': bool,
            'reason': str (如果不合法，说明原因)
        }
    """
    # 检查 1：新内容不能为空
    if not new_content or not new_content.strip():
        return {
            'valid': False,
            'reason': 'AI 生成内容为空'
        }

    # 检查 2：新内容不能与原内容完全相同
    if new_content == original_content:
        return {
            'valid': False,
            'reason': 'AI 生成内容与原内容完全相同（无需修改）'
        }

    # 检查 3：新内容长度不能小于原内容长度的 20%
    original_length = len(original_content)
    new_length = len(new_content)
    if new_length < original_length * 0.2:
        return {
            'valid': False,
            'reason': f'AI 生成内容过短（{new_length} 字符 < 原内容长度 20% {int(original_length * 0.2)} 字符）'
        }

    return {
        'valid': True,
        'reason': None
    }


def validate_modification_quality(old_content: str, new_content: str) -> dict:
    """验证修改质量是否合理

    重点检查：
    1. 是否包含元信息污染
    2. 是否破坏原有文档结构
    3. 修改范围是否合理（辅助检查）

    Args:
        old_content: 修改前的内容
        new_content: 修改后的内容

    Returns:
        dict: {
            'valid': bool,
            'reason': str (如果不合法，说明原因)
        }
    """
    # 1. 检查是否包含元信息污染（核心检查）
    forbidden_patterns = [
        "测试目标",
        "测试内容",
        "执行计划",
        "Todo List",
        "风险提示",
        "下一步",
        "Issue #",
        "### Todo List",       # 新增：模板化的 Todo List
        "### 风险提示",        # 新增：模板化的风险提示
        "### 下一步",          # 新增：模板化的下一步
        "Step 1:",              # 新增：步骤标记
        "Step 2:",              # 新增：步骤标记
        "Zhipu Fix Plan",
        "## 🤖 Zhipu",
        "由 Zhipu AI 生成",
    ]

    for pattern in forbidden_patterns:
        if pattern in new_content:
            return {
                'valid': False,
                'reason': f'包含了不应写入的内容：{pattern}'
            }

    # 2. 检查是否破坏了原有文档结构（核心检查）
    # 检查关键标题是否被保留
    old_lines = old_content.split('\n')

    # 提取原文件中的关键标题（# 和 ##）
    key_headings = []
    in_code_block = False  # 跟踪是否在 fenced code block 中（仅处理 triple backticks）

    for line in old_lines:
        line_stripped = line.strip()

        # 检测 fenced code block 的开始/结束（```）
        if line_stripped.startswith('```'):
            in_code_block = not in_code_block
            continue

        # 只在代码块外部提取标题
        if not in_code_block:
            # 只接受真正的 Markdown 标题格式：# 或 ##（后面必须有空格）
            # 继续不保护 ### 及更深层级标题
            if line_stripped.startswith('# ') or line_stripped.startswith('## '):
                # 提取标题文本（去掉 # 符号）
                heading = line_stripped.lstrip('#').strip()
                if heading and len(heading) < 50:  # 只保留长度合理的标题
                    key_headings.append({
                        'level': '#' if line_stripped.startswith('# ') else '##',
                        'text': heading
                    })

    # 检查新文件是否保留了这些关键标题
    if key_headings:
        for heading_info in key_headings:
            level = heading_info['level']
            text = heading_info['text']
            # 检查新文件是否仍包含这个标题
            expected_pattern = f"{level} {text}"
            if expected_pattern not in new_content:
                return {
                    'valid': False,
                    'reason': f'破坏了文档结构，缺少关键标题：{expected_pattern}'
                }

    # 3. 检查修改范围（辅助检查，不作为唯一标准）
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    line_diff = abs(len(new_lines) - len(old_lines))

    # 如果修改行数超过阈值，警告（但不强制拦截）
    if line_diff > 50:
        # 只记录警告，不返回 False
        print(f"  ⚠️ 注意：修改范围较大（{line_diff} 行），请确认是否合理")

    return {
        'valid': True,
        'reason': None
    }


def build_step5_success_message(
    file_path: str,
    branch_name: str,
    commit_sha: str,
    commit_message: str
) -> str:
    """构建 Step 5 修改成功时的回复消息

    Args:
        file_path: 修改的文件路径
        branch_name: 工作分支名称
        commit_sha: Commit SHA（完整）
        commit_message: Commit message 第一行

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 5 文件修改成功

**状态**: ✅ 已成功在工作分支上修改文件并提交

**修改文件**: `{file_path}`

**工作分支**: `{branch_name}`

**Commit SHA**: `{commit_sha[:7]}`

**Commit message**: `{commit_message}`

---

**⚠️ 重要提示**：

- 当前仅在工作分支上修改，尚未合并到默认分支
- 尚未创建 Draft PR（将在下一步创建）

---
🤖 Zhipu AI Stage 5 | {repo_name}
"""


def build_step5_failure_message(file_path: str, error_msg: str) -> str:
    """构建 Step 5 修改失败时的回复消息

    Args:
        file_path: 尝试修改的文件路径
        error_msg: 错误信息

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 5 文件修改失败

**状态**: ❌ 修改文件时发生错误

**目标文件**: `{file_path}`

**错误原因**: {error_msg}

---

**ℹ️ Step 1/2/3/4 已成功完成**

---
🤖 Zhipu AI Stage 5 | {repo_name}
"""


def build_step5_unsupported_file_message(file_path: str) -> str:
    """构建 Step 5 不支持的文件类型时的回复消息

    Args:
        file_path: 文件路径

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 5 跳过非支持的文件

**状态**: ⚠️ 当前目标文件暂不支持修改

**目标文件**: `{file_path}`

**原因**: 文件不在当前支持范围内

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

**配置文件使用说明**：
- `.gitignore` 和 `.env.example` 只支持 append-only 模式
- 不能修改或删除现有内容，只能在末尾追加新内容

**如何修复**：
1. 检查文件路径是否符合上述规则
2. 在 Issue 中重新评论 `@zhipu`，生成修正后的计划
3. 确保 `### 计划修改文件` 章节中的第一个文件符合规则

---

**ℹ️ Step 1/2/3/4 已成功完成**

---
🤖 Zhipu AI Stage 5 | {repo_name}
"""


def build_step5_skip_message(file_path: str, reason: str) -> str:
    """构建 Step 5 跳过修改时的回复消息

    Args:
        file_path: 文件路径
        reason: 跳过原因

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## 🤖 Stage 5 文件内容未变更

**状态**: ⚠️ AI 生成结果显示无需修改该文件

**目标文件**: `{file_path}`

**原因**: {reason}

**说明**: 未创建 commit

---

**ℹ️ Step 1/2/3/4 已成功完成**

---
🤖 Zhipu AI Stage 5 | {repo_name}
"""


def execute_step5(g, repo, issue, issue_number: int) -> dict:
    """执行 Step 5 文件修改并提交

    Args:
        g: Github client
        repo: Github repository object
        issue: Github issue object
        issue_number: Issue 编号

    Returns:
        dict: {
            'status': str,  # 'success', 'skipped', 'failed'
            'reason': str,  # 原因说明（skipped/failed 时）
            'file_path': str,  # 文件路径
            'commit_sha': str,  # Commit SHA（仅 success 时）
        }
    """
    print("🔍 准备执行文件修改...")

    # 1. 生成工作分支名称（复用 Step 3 的逻辑）
    branch_name = generate_branch_name(issue_number)
    print(f"  📌 工作分支: {branch_name}")

    # 2. 获取 Stage 1 计划（复用 Step 2 的逻辑）
    print("🔍 查找 Stage 1 计划...")
    existing_plan = get_existing_plan(issue)

    if not existing_plan:
        print("  ℹ️ 未找到 Stage 1 计划")
        reply_message = build_step5_failure_message(
            file_path="(未知)",
            error_msg="未找到 Stage 1 计划"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': '未找到 Stage 1 计划',
            'file_path': '(未知)',
            'commit_sha': None
        }

    print("  ✅ 找到 Stage 1 计划")

    # 3. 提取第一个文件路径
    print("🔍 提取第一个文件路径...")
    file_path = extract_first_file_path(existing_plan)

    if not file_path:
        print("  ℹ️ 未识别到文件路径")
        reply_message = build_step5_failure_message(
            file_path="(未知)",
            error_msg="未识别到文件路径"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': '未识别到文件路径',
            'file_path': '(未知)',
            'commit_sha': None
        }

    print(f"  ✅ 文件路径: {file_path}")

    # 4. 检查文件类型和路径安全（先检查类型和路径）
    print("🔍 检查文件类型和路径安全...")

    # 判断文件类型
    is_markdown = is_supported_markdown_file(file_path)
    is_config = is_supported_append_only_config_file(file_path)

    if not is_markdown and not is_config:
        print(f"  ℹ️ 文件 {file_path} 不在支持范围内")
        reply_message = build_step5_unsupported_file_message(file_path)
        issue.create_comment(reply_message)
        print("  ✅ 已回复跳过消息")
        return {
            'status': 'skipped',
            'reason': f'文件 {file_path} 不在支持范围内（仅支持 .md 文件和 .gitignore/.env.example 配置文件）',
            'file_path': file_path,
            'commit_sha': None
        }

    print(f"  ✅ 文件类型和路径安全检查通过")

    # 5. 验证文件是否存在（再检查存在性）
    print("🔍 验证文件是否存在...")
    if not verify_file_exists(repo, file_path):
        print(f"  ❌ 文件 {file_path} 不存在")
        reply_message = build_step5_file_not_found_message(file_path)
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'文件 {file_path} 不存在',
            'file_path': file_path,
            'commit_sha': None
        }

    print(f"  ✅ 文件存在")

    # 6. 读取文件当前内容（复用 Step 4 的逻辑）
    print(f"📖 读取文件当前内容（分支: {branch_name}）...")
    read_result = read_file_content_safe(repo, file_path, branch_name)

    if not read_result['success']:
        print(f"  ❌ 读取失败: {read_result['error']}")
        reply_message = build_step5_failure_message(file_path, read_result['error'])
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'读取文件失败: {read_result["error"]}',
            'file_path': file_path,
            'commit_sha': None
        }

    print(f"  ✅ 读取成功，文件大小: {read_result['size']} bytes")
    current_content = read_result['content']

    # 6. 构造修改目标
    print("🎯 构造修改目标...")
    modification_objective = construct_modification_objective(
        file_path=file_path,
        issue_title=issue.title
    )
    print(f"  ✅ 修改目标: {modification_objective}")

    # 7. 调用 AI 生成修改后的内容
    print("🤖 调用 AI 生成修改内容...")
    new_content = generate_modified_content(
        current_content=current_content,
        modification_objective=modification_objective,
        file_path=file_path
    )

    if not new_content:
        print("  ❌ AI 生成内容失败")
        reply_message = build_step5_failure_message(file_path, "AI 生成内容失败")
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': 'AI 生成内容失败',
            'file_path': file_path,
            'commit_sha': None
        }

    # 对于配置文件，将 AI 生成的追加内容拼接到文件末尾
    if is_config:
        print(f"  📝 检测到配置文件，使用 append-only 模式")
        print(f"  📝 AI 生成的追加内容长度: {len(new_content)} 字符")

        # 验证追加内容是否安全
        print("🔍 验证追加内容安全性...")
        append_validation = validate_append_content(file_path, new_content, current_content)

        if not append_validation['valid']:
            print(f"  ❌ 追加内容验证失败: {append_validation['reason']}")
            reply_message = build_step5_skip_message(file_path, append_validation['reason'])
            issue.create_comment(reply_message)
            print("  ✅ 已回复跳过消息")
            return {
                'status': 'skipped',
                'reason': append_validation['reason'],
                'file_path': file_path,
                'commit_sha': None
            }

        print(f"  ✅ 追加内容安全验证通过")

        # 追加内容到文件末尾（使用安全的追加函数）
        final_content = append_to_file_content(current_content, new_content)

        print(f"  ✅ 追加后的文件内容长度: {len(final_content)} 字符")
        print(f"  📊 追加了 {len(final_content) - len(current_content)} 字符")
    else:
        # Markdown 文件，使用 AI 生成的完整内容
        final_content = new_content
        print(f"  ✅ AI 生成内容长度: {len(new_content)} 字符")

    # 6.5. 验证修改质量（新增：质量控制）
    print("🔍 验证修改质量...")
    quality_check = validate_modification_quality(current_content, final_content)

    if not quality_check['valid']:
        print(f"  ❌ 质量验证失败: {quality_check['reason']}")
        reply_message = build_step5_skip_message(file_path, quality_check['reason'])
        issue.create_comment(reply_message)
        print("  ✅ 已回复跳过消息")
        return {
            'status': 'skipped',
            'reason': quality_check['reason'],
            'file_path': file_path,
            'commit_sha': None
        }

    print("  ✅ 质量验证通过")

    # 7. 验证生成内容
    print("🔍 验证生成内容...")
    validation = validate_generated_content(final_content, current_content)

    if not validation['valid']:
        print(f"  ⚠️ 验证失败: {validation['reason']}")
        reply_message = build_step5_skip_message(file_path, validation['reason'])
        issue.create_comment(reply_message)
        print("  ✅ 已回复跳过消息")
        return {
            'status': 'skipped',
            'reason': validation['reason'],
            'file_path': file_path,
            'commit_sha': None
        }

    print("  ✅ 验证通过")

    # 8. 写入文件并创建 commit
    print("💾 写入文件并创建 commit...")
    try:
        # 获取当前文件的 sha
        content_file = repo.get_contents(file_path, ref=branch_name)

        # 构建 commit message
        commit_message = f"docs/issue-{issue_number}: modify {file_path}\n\n{issue.title}\n\nRef: #{issue_number}"

        # 更新文件
        commit = repo.update_file(
            path=file_path,
            message=commit_message,
            content=final_content,
            sha=content_file.sha,
            branch=branch_name
        )

        commit_sha = commit['commit'].sha
        print(f"  ✅ Commit 创建成功: {commit_sha[:7]}")

    except Exception as e:
        print(f"  ❌ 写入文件或创建 commit 失败: {e}")
        reply_message = build_step5_failure_message(file_path, f"写入文件失败: {str(e)}")
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'写入文件失败: {str(e)}',
            'file_path': file_path,
            'commit_sha': None
        }

    # 9. 生成成功回复
    print("💬 生成成功回复...")
    reply_message = build_step5_success_message(
        file_path=file_path,
        branch_name=branch_name,
        commit_sha=commit_sha,
        commit_message=f"docs/issue-{issue_number}: modify {file_path}"
    )

    # 10. 回复到 Issue
    try:
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}")
        raise

    print(f"  ✅ Step 5 完成")

    return {
        'status': 'success',
        'reason': None,
        'file_path': file_path,
        'commit_sha': commit_sha
    }


# ==================== Stage 6: Draft PR 创建 ====================

def check_branch_divergence(repo, base_branch: str, head_branch: str) -> dict:
    """检查工作分支相对默认分支的差异

    Args:
        repo: Github repository object
        base_branch: 目标分支（默认分支）
        head_branch: 源分支（工作分支）

    Returns:
        dict: {
            'success': bool,
            'ahead_by': int,  # 工作分支领先默认分支的 commit 数
            'error': str  # 错误信息（仅失败时）
        }
    """
    try:
        print(f"  🔍 比较分支差异: {head_branch} -> {base_branch}")
        comparison = repo.compare(base_branch, head_branch)

        ahead_by = comparison.ahead_by
        print(f"  ✅ 工作分支领先 {ahead_by} 个 commit")

        return {
            'success': True,
            'ahead_by': ahead_by,
            'error': None
        }

    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ 比较分支差异失败: {error_msg}")
        return {
            'success': False,
            'ahead_by': 0,
            'error': error_msg
        }


def check_existing_pr(repo, branch_name: str) -> dict:
    """检查工作分支是否已存在 open 或 draft PR

    Args:
        repo: Github repository object
        branch_name: 工作分支名称

    Returns:
        dict: {
            'success': bool,  # 是否成功检查
            'has_existing_pr': bool,  # 是否存在 PR
            'existing_pr': object | None,  # PR 对象（如果存在）
            'error': str  # 错误信息（仅失败时）
        }

    Raises:
        Exception: 仅在明确确认"没有 open PR"时返回 success=True，否则抛出异常
    """
    try:
        print(f"  🔍 检查是否已存在 open/draft PR（分支: {branch_name}）")

        # 构建完整的 head 引用格式：owner:branch
        head_ref = f"{repo.owner.login}:{branch_name}"
        print(f"  📌 查询条件: state='open', head='{head_ref}'")

        # 查询所有 open 状态的 PR（包括 draft 和普通 open PR）
        open_prs = repo.get_pulls(state='open', head=head_ref)

        # 获取结果数量
        pr_count = open_prs.totalCount
        print(f"  ✅ 找到 {pr_count} 个 open PR")

        # 如果存在任何 open PR，返回第一个
        if pr_count > 0:
            pr = open_prs[0]  # 获取第一个 PR
            draft_status = "Draft" if pr.draft else "普通 Open"
            print(f"  ℹ️ 已存在 PR: #{pr.number} ({draft_status})")
            return {
                'success': True,
                'has_existing_pr': True,
                'existing_pr': pr,
                'error': None
            }

        # 如果没有任何 open PR，明确确认"没有 open PR"
        print(f"  ✅ 确认没有 open PR")
        return {
            'success': True,
            'has_existing_pr': False,
            'existing_pr': None,
            'error': None
        }

    except Exception as e:
        # 其他异常（API 错误、权限错误、网络错误等）继续抛出
        error_msg = str(e)
        print(f"  ❌ 检查已存在 PR 时发生异常: {error_msg}")
        # 不返回 success=False，而是直接抛出异常，让调用方处理
        raise


def create_draft_pr(
    repo,
    issue,
    branch_name: str,
    base_branch: str,
    stage1_plan: str,
    step5_commit_sha: str
) -> dict:
    """创建 Draft PR

    Args:
        repo: Github repository object
        issue: Github issue object
        branch_name: 工作分支名称
        base_branch: 默认分支名称
        stage1_plan: Stage 1 计划内容
        step5_commit_sha: Step 5 的 commit SHA（可能为 None）

    Returns:
        dict: {
            'success': bool,
            'pr': object | None,  # PR 对象（成功时）
            'error': str  # 错误信息（失败时）
        }
    """
    try:
        print("  🔨 准备创建 Draft PR...")

        # 生成 PR 标题
        issue_title = issue.title or "无标题"
        pr_title = f"[Zhipu AI] Issue #{issue.number}: {issue_title}"

        # 截断过长的标题
        if len(pr_title) > 80:
            # 保留 "[Zhipu AI] Issue #XX: " 和前 60 个字符
            prefix = f"[Zhipu AI] Issue #{issue.number}: "
            title_part = issue_title[:60] + "..."
            pr_title = prefix + title_part

        print(f"  📌 PR 标题: {pr_title}")

        # 生成 PR body（最小必要信息）
        commit_info = step5_commit_sha if step5_commit_sha else "无"
        pr_body = f"""## 🤖 Zhipu AI 自动生成的 Draft PR

### 关联信息
- **Issue**: #{issue.number} - {issue_title}
- **源分支**: `{branch_name}`
- **目标分支**: `{base_branch}`
- **Step 5 Commit**: {commit_info}

### 说明
⚠️ 此 PR 由 AI 自动生成，待人工 review 改动内容后，再决定是否标记为 Ready for review。

---
🤖 Zhipu AI Agent
"""

        # 创建 Draft PR
        print(f"  🔨 调用 GitHub API 创建 Draft PR...")
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=base_branch,
            draft=True,
            maintainer_can_modify=True
        )

        print(f"  ✅ Draft PR 创建成功: #{pr.number}")
        return {
            'success': True,
            'pr': pr,
            'error': None
        }

    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ 创建 Draft PR 失败: {error_msg}")
        return {
            'success': False,
            'pr': None,
            'error': error_msg
        }


def build_step6_success_message(
    pr_title: str,
    pr_html_url: str,
    head_branch: str,
    base_branch: str
) -> str:
    """构建 Step 6 Draft PR 创建成功时的回复消息

    Args:
        pr_title: PR 标题
        pr_html_url: PR HTML URL
        head_branch: 源分支
        base_branch: 目标分支

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## ✅ Step 6: Draft PR 创建成功

已成功创建 Draft Pull Request：

- **PR 标题**: {pr_title}
- **PR 链接**: {pr_html_url}
- **源分支**: `{head_branch}`
- **目标分支**: `{base_branch}`
- **PR 状态**: Draft（待 review）

### 📌 重要提示
⚠️ **当前 PR 尚未 merge**，请人工 review 改动内容后再决定是否 merge。

---
🤖 由 Zhipu AI Agent 自动生成 - {repo_name}
"""


def build_step6_existing_pr_message(existing_pr) -> str:
    """构建 Step 6 已存在 PR 时的回复消息

    Args:
        existing_pr: 已存在的 PR 对象

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    draft_status = "Draft" if existing_pr.draft else "普通 Open"

    return f"""## ℹ️ Step 6: PR 已存在

工作分支 `{existing_pr.head.ref}` 已存在关联的 Pull Request：

- **PR 标题**: {existing_pr.title}
- **PR 链接**: {existing_pr.html_url}
- **PR 状态**: {draft_status}

本次未创建新的 PR，请直接使用现有 PR。

---
🤖 由 Zhipu AI Agent 自动生成 - {repo_name}
"""


def build_step6_no_changes_message(branch_name: str, base_branch: str) -> str:
    """构建 Step 6 无可提交改动时的回复消息

    Args:
        branch_name: 工作分支名称
        base_branch: 默认分支名称

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## ⚠️ Step 6: 无可提交改动

工作分支 `{branch_name}` 相对默认分支 `{base_branch}` **没有可提交的改动**（ahead_by = 0）。

### 📌 可能原因
- Stage 5 创建的 commit 与默认分支内容完全一致
- 工作分支已被合并或回滚

---
🤖 由 Zhipu AI Agent 自动生成 - {repo_name}
"""


def build_step6_failure_message(error_msg: str, failure_reason: str) -> str:
    """构建 Step 6 Draft PR 创建失败时的回复消息

    Args:
        error_msg: 错误信息
        failure_reason: 失败原因说明

    Returns:
        str: Markdown 格式的回复消息
    """
    repo_name = os.getenv('REPO', '')

    return f"""## ❌ Step 6: Draft PR 创建失败

尝试创建 Draft PR 时遇到错误：

**错误信息**: {error_msg}

### 📌 失败原因
{failure_reason}

---
🤖 由 Zhipu AI Agent 自动生成 - {repo_name}
"""


def execute_step6(
    g,
    repo,
    issue,
    issue_number: int,
    branch_name: str,
    stage1_plan: str,
    step5_result: dict
) -> dict:
    """执行 Step 6 创建 Draft PR

    Args:
        g: Github client
        repo: Github repository object
        issue: Github issue object
        issue_number: Issue 编号
        branch_name: 工作分支名称
        stage1_plan: Stage 1 计划内容
        step5_result: Step 5 的返回结果

    Returns:
        dict: {
            'status': str,  # 'success', 'skipped', 'failed'
            'reason': str,  # 原因说明（skipped/failed 时）
            'pr_url': str,  # PR URL（仅 success 时）
        }
    """
    print("🔍 准备创建 Draft PR...")

    # 1. 获取默认分支
    print("📌 获取默认分支...")
    try:
        base_branch = get_default_branch(repo)
        print(f"  ✅ 默认分支: {base_branch}")
    except Exception as e:
        print(f"  ❌ 获取默认分支失败: {e}")
        reply_message = build_step6_failure_message(
            error_msg=str(e),
            failure_reason="无法获取仓库默认分支"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': '获取默认分支失败',
            'pr_url': None
        }

    # 2. 检查分支差异
    print("🔍 检查工作分支相对默认分支的差异...")
    divergence = check_branch_divergence(repo, base_branch, branch_name)

    if not divergence['success']:
        print(f"  ❌ 检查分支差异失败")
        reply_message = build_step6_failure_message(
            error_msg=divergence['error'],
            failure_reason="无法比较分支差异，可能工作分支不存在"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'检查分支差异失败: {divergence["error"]}',
            'pr_url': None
        }

    ahead_by = divergence['ahead_by']

    # 3. 判断是否有可提交的改动
    if ahead_by == 0:
        print(f"  ℹ️ 工作分支没有领先 commit（ahead_by = 0）")
        reply_message = build_step6_no_changes_message(branch_name, base_branch)
        issue.create_comment(reply_message)
        print("  ✅ 已回复无改动消息")
        return {
            'status': 'skipped',
            'reason': '工作分支相对默认分支没有可提交的改动',
            'pr_url': None
        }

    print(f"  ✅ 工作分支领先 {ahead_by} 个 commit，可以创建 PR")

    # 4. 检查是否已存在 PR
    print("🔍 检查是否已存在 open/draft PR...")
    try:
        existing_pr_check = check_existing_pr(repo, branch_name)

        if existing_pr_check['has_existing_pr']:
            existing_pr = existing_pr_check['existing_pr']
            print(f"  ℹ️ 已存在 PR: #{existing_pr.number}")
            reply_message = build_step6_existing_pr_message(existing_pr)
            issue.create_comment(reply_message)
            print("  ✅ 已回复已存在 PR 消息")
            return {
                'status': 'skipped',
                'reason': f'已存在 PR #{existing_pr.number}',
                'pr_url': existing_pr.html_url
            }

        print(f"  ✅ 确认没有已存在的 PR")

    except Exception as e:
        print(f"  ❌ 检查已存在 PR 时发生异常: {e}")
        reply_message = build_step6_failure_message(
            error_msg=str(e),
            failure_reason="检查已存在 PR 时发生异常"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'检查已存在 PR 失败: {str(e)}',
            'pr_url': None
        }

    # 5. 创建 Draft PR
    print("🔨 创建 Draft PR...")
    step5_commit_sha = step5_result.get('commit_sha') if step5_result else None
    pr_result = create_draft_pr(
        repo=repo,
        issue=issue,
        branch_name=branch_name,
        base_branch=base_branch,
        stage1_plan=stage1_plan,
        step5_commit_sha=step5_commit_sha
    )

    if not pr_result['success']:
        print(f"  ❌ 创建 Draft PR 失败")
        reply_message = build_step6_failure_message(
            error_msg=pr_result['error'],
            failure_reason="GitHub API 返回错误，可能权限不足或参数错误"
        )
        issue.create_comment(reply_message)
        print("  ✅ 已回复失败消息")
        return {
            'status': 'failed',
            'reason': f'创建 Draft PR 失败: {pr_result["error"]}',
            'pr_url': None
        }

    pr = pr_result['pr']
    print(f"  ✅ Draft PR 创建成功: #{pr.number}")

    # 6. 生成成功回复
    print("💬 生成成功回复...")
    reply_message = build_step6_success_message(
        pr_title=pr.title,
        pr_html_url=pr.html_url,
        head_branch=branch_name,
        base_branch=base_branch
    )

    # 7. 回复到 Issue
    try:
        issue.create_comment(reply_message)
        print("  ✅ 成功回复到 Issue")
    except Exception as e:
        print(f"  ❌ 回复失败: {e}")
        raise

    print(f"  ✅ Step 6 完成")

    return {
        'status': 'success',
        'reason': None,
        'pr_url': pr.html_url
    }


if __name__ == "__main__":
    main()
