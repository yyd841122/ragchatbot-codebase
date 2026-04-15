#!/usr/bin/env python3
"""
代码格式化脚本
自动格式化代码以符合项目规范
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str):
    """运行命令"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"警告: 命令执行失败，返回码: {result.returncode}")
    return result.returncode == 0


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

    print(f"项目根目录: {project_root}")
    print(f"Backend 目录: {backend_dir}")

    if not backend_dir.exists():
        print(f"错误: backend 目录不存在: {backend_dir}")
        return 1

    # 格式化步骤
    steps = [
        # 1. 使用 black 格式化代码
        (
            ["uv", "run", "black", str(backend_dir)],
            "Black 代码格式化"
        ),
        # 2. 使用 isort 排序导入
        (
            ["uv", "run", "isort", str(backend_dir)],
            "isort 导入排序"
        ),
    ]

    print("\n开始代码格式化...")
    print("="*60)

    for cmd, description in steps:
        success = run_command(cmd, description)
        if not success:
            print(f"警告: {description} 可能存在问题")

    print("\n" + "="*60)
    print("[SUCCESS] 代码格式化完成！")
    print("="*60)

    # 运行检查验证
    print("\n运行质量检查验证...")
    check_script = project_root / "scripts" / "check_quality.py"
    if check_script.exists():
        result = subprocess.run([sys.executable, str(check_script)])
        return result.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
