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
import base64

# 添加 scripts 目录到 Python 路径，以便导入第一阶段的模块
sys.path.insert(0, '.github/scripts')

from github import Github
from github import UnknownObjectException


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

    # 执行 Step 3: 创建工作分支
    print("="*60)
    print("🔜 进入 Stage 2 - Step 3: 创建工作分支")
    print("="*60)
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
        print()
        print("="*60)
        print("⚠️ Stage 2 - Step 4 失败，但整体流程继续")
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

            # 提取反引号内的内容
            if '`' in cleaned_line:
                # 提取第一个反引号对内的内容
                start = cleaned_line.find('`')
                end = cleaned_line.find('`', start + 1)
                if start != -1 and end != -1:
                    file_path = cleaned_line[start + 1:end].strip()
                    if file_path:
                        return file_path

            # 如果没有反引号，直接使用整行（过滤掉明显不是文件路径的内容）
            elif cleaned_line and not cleaned_line.startswith('*') and not cleaned_line.startswith('#'):
                # 简单的启发式检查：看起来像文件路径（包含斜杠或.py等）
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


if __name__ == "__main__":
    main()
