#!/bin/bash
# Zhipu AI 自动化设置脚本

set -e

echo "🤖 Zhipu AI 自动化 Issue 处理系统 - 设置向导"
echo "================================================"

# 检查必要的命令
check_commands() {
    echo "📋 检查必要的命令..."
    for cmd in git gh python3; do
        if ! command -v $cmd &> /dev/null; then
            echo "❌ $cmd 未找到。请安装后再继续。"
            exit 1
        fi
    done
    echo "✅ 所有必要命令已找到"
}

# 检查 GitHub 认证
check_github_auth() {
    echo "🔐 检查 GitHub 认证..."
    if ! gh auth status &> /dev/null; then
        echo "❌ 未找到 GitHub 认证。"
        echo "请运行: gh auth login"
        exit 1
    fi
    echo "✅ GitHub 认证已找到"
}

# 获取 Zhipu API Key
get_api_key() {
    echo "🔑 请输入你的 Zhipu AI API Key:"
    echo "   (从 https://open.bigmodel.cn/usercenter/apikeys 获取)"
    read -s ZHIPU_API_KEY
    echo ""

    if [ -z "$ZHIPU_API_KEY" ]; then
        echo "❌ API Key 不能为空"
        exit 1
    fi

    echo "✅ API Key 已获取"
}

# 设置 GitHub Secrets
setup_secrets() {
    echo "🔧 设置 GitHub Secrets..."

    # 获取仓库名称
    REPO_FULL_NAME=$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
    REPO_OWNER=$(echo $REPO_FULL_NAME | cut -d'/' -f1)
    REPO_NAME=$(echo $REPO_full_NAME | cut -d'/' -f2)

    echo "   仓库名称: $REPO_FULL_NAME"

    # 设置 Zhipu API Key
    echo $ZHIPU_API_KEY | gh secret set ZHIPU_API_KEY --repo $REPO_FULL_NAME

    if [ $? -eq 0 ]; then
        echo "✅ ZHIPU_API_KEY secret 已设置"
    else
        echo "❌ 设置 secret 失败"
        exit 1
    fi
}

# 创建必要的目录结构
setup_directories() {
    echo "📁 创建必要的目录..."
    mkdir -p .github/scripts
    mkdir -p .github/workflows
    echo "✅ 目录结构已创建"
}

# 设置脚本权限
setup_permissions() {
    echo "🔐 设置脚本权限..."
    chmod +x .github/scripts/*.py 2>/dev/null || true
    echo "✅ 权限已设置"
}

# 提交更改到 Git
commit_changes() {
    echo "📝 提交更改到 Git..."

    git add .github/workflows/claude-issue-handler.yml
    git add .github/scripts/claude_issue_handler.py
    git add .github/CLAUDE_AUTOMATION.md
    git add setup_automation.sh

    git commit -m "Add Claude AI automation for issue handling" || {
        echo "⚠️  没有新的更改需要提交"
    }

    echo "✅ 更改已提交"
}

# 推送到 GitHub
push_changes() {
    echo "🚀 推送更改到 GitHub..."
    read -p "是否现在推送到 GitHub? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "✅ 更改已推送到 GitHub"
    else
        echo "⏭️  跳过推送步骤"
    fi
}

# 创建示例 Issue
create_example_issue() {
    echo "📝 创建示例 Issue..."
    read -p "是否创建示例 Issue 来测试系统? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh issue create \
            --title "🔧 Claude AI 自动化测试" \
            --label "claude-auto,enhancement" \
            --body "这是一个测试 Issue，用于验证 Claude AI 自动化系统。

### 任务
测试 Claude AI 是否能够：
1. 分析这个 Issue
2. 理解任务要求
3. 生成相应的代码或文档
4. 创建 Pull Request

### 预期结果
Claude AI 应该能够在仓库中添加一个简单的 README 更新或文档改进。"
        echo "✅ 示例 Issue 已创建"
    else
        echo "⏭️  跳过创建示例 Issue"
    fi
}

# 主执行流程
main() {
    check_commands
    check_github_auth
    get_api_key
    setup_directories
    setup_permissions
    setup_secrets
    commit_changes
    push_changes
    create_example_issue

    echo ""
    echo "🎉 设置完成！"
    echo ""
    echo "📚 使用指南："
    echo "1. 给任何 Issue 添加 'claude-auto' 标签来触发自动处理"
    echo "2. 或者手动在 GitHub Actions 页面触发工作流"
    echo "3. Claude AI 会在 Issue 中更新进度"
    echo "4. 审核自动生成的 Pull Request"
    echo ""
    echo "📖 详细文档: .github/CLAUDE_AUTOMATION.md"
}

# 运行主程序
main