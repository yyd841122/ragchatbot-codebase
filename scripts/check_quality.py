#!/usr/bin/env python3
"""
代码质量检查脚本
运行所有代码质量检查工具
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """运行命令并返回是否成功"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

    # 检查列表
    checks = [
        # 代码格式化检查
        (
            ["uv", "run", "black", "--check", str(backend_dir)],
            "Black 代码格式检查"
        ),
        # 导入排序检查
        (
            ["uv", "run", "isort", "--check-only", str(backend_dir)],
            "isort 导入排序检查"
        ),
        # 代码风格检查 (使用 .flake8 配置文件)
        (
            ["uv", "run", "flake8", str(backend_dir), "--config", str(project_root / ".flake8")],
            "Flake8 代码风格检查"
        ),
    ]

    results = []
    for cmd, description in checks:
        success = run_command(cmd, description)
        results.append((description, success))

    # 打印总结
    print(f"\n{'='*60}")
    print("检查结果总结")
    print('='*60)

    all_passed = True
    for description, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{description}: {status}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] 所有检查通过！")
        return 0
    else:
        print("\n[ERROR] 部分检查失败，请修复后重试")
        print("\n提示: 运行 'python scripts/format.py' 自动修复格式问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
