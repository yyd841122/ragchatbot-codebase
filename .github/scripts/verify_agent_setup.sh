#!/bin/bash
# 快速验证脚本 - 检查所有必需的文件和配置

echo "🔍 验证 Zhipu Issue Agent 配置..."
echo ""

# 检查文件是否存在
echo "📁 检查文件..."
files=(
  ".github/workflows/zhipu-agent-issue.yml"
  ".github/requirements-agent.txt"
  ".github/scripts/agent_issue_handler.py"
)

all_exist=true
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (不存在)"
    all_exist=false
  fi
done

echo ""

# 检查 .env 文件中的 ZHIPU_API_KEY
echo "🔑 检查环境变量..."
if [ -f ".env" ]; then
  if grep -q "ZHIPU_API_KEY=" .env; then
    echo "  ✅ ZHIPU_API_KEY 已配置"
  else
    echo "  ⚠️  ZHIPU_API_KEY 未在 .env 中配置"
    echo "     提示: GitHub Secrets 中仍需配置此变量"
  fi
else
  echo "  ⚠️  .env 文件不存在"
fi

echo ""

# 检查 Python 脚本语法
echo "🐍 检查 Python 脚本语法..."
if python3 -m py_compile .github/scripts/agent_issue_handler.py 2>/dev/null; then
  echo "  ✅ agent_issue_handler.py 语法正确"
else
  echo "  ❌ agent_issue_handler.py 语法错误"
  all_exist=false
fi

echo ""

# 总结
if [ "$all_exist" = true ]; then
  echo "🎉 所有检查通过！"
  echo ""
  echo "📚 下一步："
  echo "  1. 确保在 GitHub Secrets 中配置了 ZHIPU_API_KEY"
  echo "  2. 在任意 Issue 中评论 '@zhipu' 测试"
  echo "  3. 查看 Actions 标签页监控运行状态"
  echo ""
  echo "📖 详细文档: ZHIPU_GUIDE.md"
else
  echo "❌ 部分检查失败，请检查上述错误"
fi
