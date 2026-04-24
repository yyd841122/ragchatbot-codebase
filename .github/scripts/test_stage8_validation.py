#!/usr/bin/env python3
"""
Stage 8.1 本地逻辑测试
测试新增的路径安全检查函数和 Stage 1 校验逻辑
"""

import sys
import io

# 设置标准输出编码为 UTF-8（修复 Windows PowerShell 兼容性）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, '.github/scripts')

# 导入测试的函数
from agent_issue_executor import is_safe_path, is_supported_markdown_file
from agent_issue_handler import is_safe_path as handler_is_safe_path
from agent_issue_handler import is_supported_markdown_file as handler_is_supported_markdown_file
from agent_issue_handler import validate_first_file_exists

# Mock GitHub Repository 对象
class MockRepo:
    """Mock GitHub Repository 对象，用于测试文件存在性"""
    def __init__(self, existing_files):
        self.existing_files = existing_files

    def get_contents(self, path):
        """模拟 GitHub API 的 get_contents"""
        if path in self.existing_files:
            return True  # 文件存在
        else:
            from github import UnknownObjectException
            raise UnknownObjectException(404, {'message': 'Not Found'})


def test_is_safe_path():
    """测试路径安全检查"""
    print("🧪 测试 is_safe_path()...")

    # 正常样本
    assert is_safe_path("README.md") == True, "❌ README.md 应该安全"
    assert is_safe_path("CHANGELOG.md") == True, "❌ CHANGELOG.md 应该安全"
    assert is_safe_path("docs/GUIDE.md") == True, "❌ docs/GUIDE.md 应该安全"
    assert is_safe_path("docs/FAQ.md") == True, "❌ docs/FAQ.md 应该安全"

    # 异常样本
    assert is_safe_path("") == False, "❌ 空路径应该不安全"
    assert is_safe_path("  ") == False, "❌ 空白路径应该不安全"
    assert is_safe_path("/etc/file.md") == False, "❌ 绝对路径应该不安全"
    assert is_safe_path("../README.md") == False, "❌ 相对路径跳转应该不安全"
    assert is_safe_path("../../secret.md") == False, "❌ 多层跳转应该不安全"
    assert is_safe_path("docs/deep/file.md") == False, "❌ 深层目录应该不安全"
    assert is_safe_path("docs/a/b/c.md") == False, "❌ 多层嵌套应该不安全"

    print("  ✅ is_safe_path() 测试通过\n")


def test_is_supported_markdown_file():
    """测试文件类型检查"""
    print("🧪 测试 is_supported_markdown_file()...")

    # 正常样本
    assert is_supported_markdown_file("README.md") == True, "❌ README.md 应该支持"
    assert is_supported_markdown_file("CHANGELOG.md") == True, "❌ CHANGELOG.md 应该支持"
    assert is_supported_markdown_file("docs/GUIDE.md") == True, "❌ docs/GUIDE.md 应该支持"

    # 异常样本
    assert is_supported_markdown_file("config.py") == False, "❌ .py 文件不应该支持"
    assert is_supported_markdown_file(".env.example") == False, "❌ .env.example 不应该支持"
    assert is_supported_markdown_file("docs/deep/file.md") == False, "❌ 深层目录不应该支持"
    assert is_supported_markdown_file("../README.md") == False, "❌ 相对路径不应该支持"

    print("  ✅ is_supported_markdown_file() 测试通过\n")


def test_validate_first_file_exists():
    """测试 Stage 1 的第一个文件校验逻辑"""
    print("🧪 测试 validate_first_file_exists()...")

    # 创建 Mock Repo，模拟存在的文件
    existing_files = [
        "README.md",
        "CHANGELOG.md",
        "STAGE8_PLAN.md",
        "docs/CODE_QUALITY.md",
        "docs/QUALITY_SETUP_COMPLETE.md",
    ]
    mock_repo = MockRepo(existing_files)

    # 测试 1：CHANGELOG.md 应该通过
    print("  📝 测试 1：CHANGELOG.md")
    plan1 = "## 计划\n\n### 计划修改文件\n- `CHANGELOG.md` - 追加版本记录"
    passed1, error1 = validate_first_file_exists(plan1, mock_repo)
    assert passed1 == True, f"❌ CHANGELOG.md 应该通过，但错误: {error1}"
    print("    ✅ CHANGELOG.md 通过")

    # 测试 2：docs/CODE_QUALITY.md 应该通过
    print("  📝 测试 2：docs/CODE_QUALITY.md")
    plan2 = "## 计划\n\n### 计划修改文件\n- `docs/CODE_QUALITY.md` - 添加检查项"
    passed2, error2 = validate_first_file_exists(plan2, mock_repo)
    assert passed2 == True, f"❌ docs/CODE_QUALITY.md 应该通过，但错误: {error2}"
    print("    ✅ docs/CODE_QUALITY.md 通过")

    # 测试 3：config.py 应该失败（文件类型不支持）
    print("  📝 测试 3：config.py")
    plan3 = "## 计划\n\n### 计划修改文件\n- `config.py` - 修改配置"
    passed3, error3 = validate_first_file_exists(plan3, mock_repo)
    assert passed3 == False, f"❌ config.py 应该失败，但通过了"
    assert "不在当前支持范围内" in error3, f"❌ 错误信息应该提示'不在当前支持范围内'，但: {error3}"
    print("    ✅ config.py 正确拒绝")

    # 测试 4：../README.md 应该失败（相对路径跳转）
    print("  📝 测试 4：../README.md")
    plan4 = "## 计划\n\n### 计划修改文件\n- `../README.md` - 测试"
    passed4, error4 = validate_first_file_exists(plan4, mock_repo)
    assert passed4 == False, f"❌ ../README.md 应该失败，但通过了"
    assert "不在当前支持范围内" in error4, f"❌ 错误信息应该提示'不在当前支持范围内'，但: {error4}"
    print("    ✅ ../README.md 正确拒绝")

    # 测试 5：docs/deep/file.md 应该失败（深层目录）
    print("  📝 测试 5：docs/deep/file.md")
    plan5 = "## 计划\n\n### 计划修改文件\n- `docs/deep/file.md` - 测试"
    passed5, error5 = validate_first_file_exists(plan5, mock_repo)
    assert passed5 == False, f"❌ docs/deep/file.md 应该失败，但通过了"
    assert "不在当前支持范围内" in error5, f"❌ 错误信息应该提示'不在当前支持范围内'，但: {error5}"
    print("    ✅ docs/deep/file.md 正确拒绝")

    # 测试 6：NONEXIST.md 应该失败（文件不存在）
    print("  📝 测试 6：NONEXIST.md")
    plan6 = "## 计划\n\n### 计划修改文件\n- `NONEXIST.md` - 测试"
    passed6, error6 = validate_first_file_exists(plan6, mock_repo)
    assert passed6 == False, f"❌ NONEXIST.md 应该失败，但通过了"
    assert "不存在" in error6, f"❌ 错误信息应该提示'不存在'，但: {error6}"
    print("    ✅ NONEXIST.md 正确拒绝")

    print("  ✅ validate_first_file_exists() 测试通过\n")


def test_function_consistency():
    """测试 executor 和 handler 的函数逻辑一致性"""
    print("🧪 测试 executor 和 handler 函数一致性...")

    # 测试 is_safe_path() 的一致性
    # 注意：is_safe_path() 只检查路径安全性，不检查文件类型
    safe_path_test_cases = [
        ("README.md", True),           # 安全路径
        ("CHANGELOG.md", True),        # 安全路径
        ("docs/GUIDE.md", True),       # 安全路径
        ("config.py", True),           # 安全路径（虽然不是 .md，但路径本身安全）
        ("../README.md", False),       # 相对路径跳转
        ("docs/deep/file.md", False),  # 深层目录
    ]

    for file_path, expected in safe_path_test_cases:
        result1 = is_safe_path(file_path)
        result2 = handler_is_safe_path(file_path)
        assert result1 == result2 == expected, f"❌ is_safe_path({file_path}): executor={result1}, handler={result2}, expected={expected}"

    # 测试 is_supported_markdown_file() 的一致性
    # 注意：is_supported_markdown_file() 检查文件类型 + 路径安全性
    markdown_file_test_cases = [
        ("README.md", True),           # .md 文件，路径安全
        ("CHANGELOG.md", True),        # .md 文件，路径安全
        ("docs/GUIDE.md", True),       # .md 文件，路径安全
        ("config.py", False),          # 非 .md 文件
        ("../README.md", False),       # 相对路径跳转
        ("docs/deep/file.md", False),  # 深层目录
    ]

    for file_path, expected in markdown_file_test_cases:
        result1 = is_supported_markdown_file(file_path)
        result2 = handler_is_supported_markdown_file(file_path)
        assert result1 == result2 == expected, f"❌ is_supported_markdown_file({file_path}): executor={result1}, handler={result2}, expected={expected}"

    print("  ✅ executor 和 handler 函数逻辑一致\n")


if __name__ == "__main__":
    try:
        print("="*60)
        print("🚀 Stage 8.1 本地逻辑测试开始")
        print("="*60 + "\n")

        test_is_safe_path()
        test_is_supported_markdown_file()
        test_validate_first_file_exists()
        test_function_consistency()

        print("="*60)
        print("✅ 所有本地逻辑测试通过")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
