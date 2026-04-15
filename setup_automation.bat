@echo off
REM Claude AI 自动化设置脚本 (Windows)

echo 🤖 Claude AI 自动化 Issue 处理系统 - 设置向导
echo ================================================

REM 检查必要命令
echo 📋 检查必要命令...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ git 未找到。请安装后再继续。
    exit /b 1
)

where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ gh 未找到。请安装 GitHub CLI 后再继续。
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ python 未找到。请安装 Python 后再继续。
    exit /b 1
)

echo ✅ 所有必要命令已找到

REM 检查 GitHub 认证
echo 🔐 检查 GitHub 认证...
gh auth status >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未找到 GitHub 认证。
    echo 请运行: gh auth login
    exit /b 1
)
echo ✅ GitHub 认证已找到

REM 获取 Anthropic API Key
echo 🔑 请输入你的 Anthropic API Key:
echo    (从 https://console.anthropic.com 获取)
set /p ANTHROPIC_API_KEY=""

if "%ANTHROPIC_API_KEY%"=="" (
    echo ❌ API Key 不能为空
    exit /b 1
)

echo ✅ API Key 已获取

REM 设置 GitHub Secrets
echo 🔧 设置 GitHub Secrets...

REM 获取仓库名称
for /f "delims=" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
for /f "tokens=2 delims=:/." %%a in ("%REMOTE_URL%") do set OWNER=%%a
for /f "tokens=3 delims=/" %%a in ("%REMOTE_URL%") do set REPO=%%a
set REPO_FULL_NAME=%OWNER%/%REPO%

echo    仓库名称: %REPO_FULL_NAME%

REM 设置 Anthropic API Key
echo %ANTHROPIC_API_KEY% | gh secret set ANTHROPIC_API_KEY --repo %REPO_FULL_NAME%

if %errorlevel% neq 0 (
    echo ❌ 设置 secret 失败
    exit /b 1
)

echo ✅ ANTHROPIC_API_KEY secret 已设置

REM 创建必要的目录结构
echo 📁 创建必要的目录...
if not exist ".github\scripts" mkdir .github\scripts
if not exist ".github\workflows" mkdir .github\workflows
echo ✅ 目录结构已创建

REM 提交更改到 Git
echo 📝 提交更改到 Git...

git add .github/workflows/claude-issue-handler.yml
git add .github/scripts/claude_issue_handler.py
git add .github/CLAUDE_AUTOMATION.md
git add setup_automation.bat

git commit -m "Add Claude AI automation for issue handling" >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  没有新的更改需要提交
) else (
    echo ✅ 更改已提交
)

REM 推送到 GitHub
echo 🚀 推送更改到 GitHub...
set /p PUSH_CONFIRM="是否现在推送到 GitHub? (y/n): "
if /i "%PUSH_CONFIRM%"=="y" (
    git push origin main
    echo ✅ 更改已推送到 GitHub
) else (
    echo ⏭️  跳过推送步骤
)

REM 创建示例 Issue
echo 📝 创建示例 Issue...
set /p ISSUE_CONFIRM="是否创建示例 Issue 来测试系统? (y/n): "
if /i "%ISSUE_CONFIRM%"=="y" (
    gh issue create ^
        --title "🔧 Claude AI 自动化测试" ^
        --label "claude-auto,enhancement" ^
        --body "这是一个测试 Issue，用于验证 Claude AI 自动化系统。

### 任务
测试 Claude AI 是否能够：
1. 分析这个 Issue
2. 理解任务要求
3. 生成相应的代码或文档
4. 创建 Pull Request

### 预期结果
Claude AI 应该能够在仓库中添加一个简单的 README 更新或文档改进。"

    if %errorlevel% equ 0 (
        echo ✅ 示例 Issue 已创建
    ) else (
        echo ❌ 创建 Issue 失败
    )
) else (
    echo ⏭️  跳过创建示例 Issue
)

echo.
echo 🎉 设置完成！
echo.
echo 📚 使用指南：
echo 1. 给任何 Issue 添加 'claude-auto' 标签来触发自动处理
echo 2. 或者手动在 GitHub Actions 页面触发工作流
echo 3. Claude AI 会在 Issue 中更新进度
echo 4. 审核自动生成的 Pull Request
echo.
echo 📖 详细文档: .github\CLAUDE_AUTOMATION.md

pause