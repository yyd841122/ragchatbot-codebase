#!/usr/bin/env python3
"""
本地测试脚本 - 模拟 GitHub Actions 环境运行 agent_issue_handler.py

使用方法：
1. 确保 .env 文件中有 ZHIPU_API_KEY
2. 运行: python .github/scripts/test_agent_issue_local.py
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def load_env():
    """加载 .env 文件"""
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def main():
    """主函数"""
    print("🧪 本地测试 Zhipu Issue Agent\n")

    # 加载环境变量
    load_env()

    # 检查必需的环境变量
    required_vars = {
        "ZHIPU_API_KEY": "智谱 AI API Key",
    }

    missing_vars = []
    for var_name, description in required_vars.items():
        if var_name not in os.environ:
            missing_vars.append(f"  - {var_name} ({description})")

    if missing_vars:
        print("❌ 缺少必需的环境变量：")
        print("\n".join(missing_vars))
        print("\n请在 .env 文件中添加这些变量")
        return 1

    # 设置 GitHub 环境变量（模拟 GitHub Actions 环境）
    # 注意：你需要手动提供这些值
    print("📝 请提供测试用的 GitHub 信息：\n")

    repo = input("仓库 (格式: owner/repo, 默认: yyd841122/starting-ragchatbot): ").strip()
    if not repo:
        repo = "yyd841122/starting-ragchatbot"

    issue_number = input("Issue 编号 (默认: 1): ").strip()
    if not issue_number:
        issue_number = "1"

    comment_body = input("评论内容 (默认: '@zhipu'): ").strip()
    if not comment_body:
        comment_body = "@zhipu"

    comment_author = input("评论者 (默认: test-user): ").strip()
    if not comment_author:
        comment_author = "test-user"

    # 设置环境变量
    os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "")
    os.environ["REPO"] = repo
    os.environ["ISSUE_NUMBER"] = issue_number
    os.environ["COMMENT_BODY"] = comment_body
    os.environ["COMMENT_AUTHOR"] = comment_author

    print("\n" + "="*60)
    print("🚀 开始运行 Agent...\n")

    # 导入并运行 agent
    try:
        from agent_issue_handler import main as agent_main
        agent_main()
        return 0
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
