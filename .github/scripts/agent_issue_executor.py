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

    # 完成
    print("="*60)
    print("✅ Stage 2 - Step 1 完成!")
    print("="*60)
    print()
    print("📊 本次执行内容:")
    print("  ✅ 识别 /zhipu-apply 触发")
    print("  ✅ 读取 Issue 上下文")
    print("  ✅ 输出 Stage 2 日志")
    print("  ✅ 回复预备流程评论")
    print()
    print("🔜 下一步: 实现 Step 2 - 读取 Issue 和生成计划")
    print()


if __name__ == "__main__":
    main()
