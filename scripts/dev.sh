#!/bin/bash
# 开发工具快捷脚本
# Usage: ./scripts/dev.sh [command]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

case "${1:-help}" in
    format)
        echo "运行代码格式化..."
        python scripts/format.py
        ;;
    check)
        echo "运行质量检查..."
        python scripts/check_quality.py
        ;;
    test)
        echo "运行测试..."
        cd backend && uv run pytest -v
        ;;
    serve)
        echo "启动开发服务器..."
        cd backend && uv run uvicorn app:app --reload --port 8000
        ;;
    *)
        echo "开发工具快捷脚本"
        echo ""
        echo "用法: ./scripts/dev.sh [command]"
        echo ""
        echo "可用命令:"
        echo "  format  - 格式化所有代码"
        echo "  check   - 运行代码质量检查"
        echo "  test    - 运行测试套件"
        echo "  serve   - 启动开发服务器"
        echo ""
        ;;
esac
