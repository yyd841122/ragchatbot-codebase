#!/usr/bin/env python3
"""
Stage 8.2 本地逻辑测试
测试新增的配置文件 append-only 支持逻辑
"""

import sys
import io

# 设置标准输出编码为 UTF-8（修复 Windows PowerShell 兼容性）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, '.github/scripts')

# 导入测试的函数
from agent_issue_executor import (
    is_safe_path,
    is_supported_markdown_file,
    is_supported_append_only_config_file,
    _get_last_n_lines,
    construct_modification_objective,
    validate_append_content,
    append_to_file_content,
)
from agent_issue_handler import (
    is_safe_path as handler_is_safe_path,
    is_supported_markdown_file as handler_is_supported_markdown_file,
    is_supported_append_only_config_file as handler_is_supported_append_only_config_file,
    validate_first_file_exists,
)

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


def test_is_supported_append_only_config_file():
    """测试配置文件类型检查"""
    print("🧪 测试 is_supported_append_only_config_file()...")

    # 正常样本（根目录）
    assert is_supported_append_only_config_file(".gitignore") == True, "❌ .gitignore 应该支持"
    assert is_supported_append_only_config_file(".env.example") == True, "❌ .env.example 应该支持"

    # 异常样本（子目录）
    assert is_supported_append_only_config_file("config/.gitignore") == False, "❌ 子目录的 .gitignore 不应该支持"
    assert is_supported_append_only_config_file("docs/.env.example") == False, "❌ 子目录的 .env.example 不应该支持"

    # 异常样本（其他文件）
    assert is_supported_append_only_config_file("README.md") == False, "❌ README.md 不应该作为配置文件支持"
    assert is_supported_append_only_config_file("requirements.txt") == False, "❌ requirements.txt 不应该支持"
    assert is_supported_append_only_config_file("config.py") == False, "❌ config.py 不应该支持"

    # 异常样本（路径安全）
    assert is_supported_append_only_config_file("../.gitignore") == False, "❌ 相对路径不应该支持"
    assert is_supported_append_only_config_file("/etc/.gitignore") == False, "❌ 绝对路径不应该支持"

    print("  ✅ is_supported_append_only_config_file() 测试通过\n")


def test_function_consistency():
    """测试 executor 和 handler 的函数逻辑一致性"""
    print("🧪 测试 executor 和 handler 函数一致性...")

    # 测试 is_supported_append_only_config_file() 的一致性
    config_file_test_cases = [
        (".gitignore", True),
        (".env.example", True),
        ("config/.gitignore", False),
        ("README.md", False),
        ("requirements.txt", False),
    ]

    for file_path, expected in config_file_test_cases:
        result1 = is_supported_append_only_config_file(file_path)
        result2 = handler_is_supported_append_only_config_file(file_path)
        assert result1 == result2 == expected, f"❌ is_supported_append_only_config_file({file_path}): executor={result1}, handler={result2}, expected={expected}"

    print("  ✅ executor 和 handler 函数逻辑一致\n")


def test_construct_modification_objective():
    """测试修改目标构造逻辑"""
    print("🧪 测试 construct_modification_objective()...")

    # 测试配置文件
    obj1 = construct_modification_objective(".gitignore", "添加忽略规则")
    assert "追加" in obj1, "❌ .gitignore 应该包含'追加'"
    assert "只返回要追加的内容" in obj1, "❌ .gitignore 应该明确说明只返回追加内容"

    obj2 = construct_modification_objective(".env.example", "添加环境变量")
    assert "追加" in obj2, "❌ .env.example 应该包含'追加'"
    assert "只返回要追加的内容" in obj2, "❌ .env.example 应该明确说明只返回追加内容"

    # 测试 Markdown 文件（应该保持原有逻辑）
    obj3 = construct_modification_objective("README.md", "测试")
    assert "README.md" in obj3, "❌ README.md 目标应该包含文件名"

    print("  ✅ construct_modification_objective() 测试通过\n")


def test_get_last_n_lines():
    """测试获取最后 N 行的函数"""
    print("🧪 测试 _get_last_n_lines()...")

    # 测试正常情况
    content = "line1\nline2\nline3\nline4\nline5"
    result = _get_last_n_lines(content, 2)
    assert result == "line4\nline5", f"❌ 应该返回最后 2 行，但返回: {result}"

    # 测试行数不足的情况
    result = _get_last_n_lines(content, 10)
    assert result == content, "❌ 行数不足时应该返回全部内容"

    # 测试空内容
    result = _get_last_n_lines("", 5)
    assert result == "", "❌ 空内容应该返回空字符串"

    print("  ✅ _get_last_n_lines() 测试通过\n")


def test_validate_first_file_with_config():
    """测试 Stage 1 的第一个文件校验逻辑（包含配置文件）"""
    print("🧪 测试 validate_first_file_exists()（包含配置文件）...")

    # 创建 Mock Repo，模拟存在的文件
    existing_files = [
        "README.md",
        "CHANGELOG.md",
        ".gitignore",
        ".env.example",
        "docs/GUIDE.md",
    ]
    mock_repo = MockRepo(existing_files)

    # 测试 1：.gitignore 应该通过
    print("  📝 测试 1：.gitignore")
    plan1 = "## 计划\n\n### 计划修改文件\n- `.gitignore` - 追加忽略规则"
    passed1, error1 = validate_first_file_exists(plan1, mock_repo)
    assert passed1 == True, f"❌ .gitignore 应该通过，但错误: {error1}"
    print("    ✅ .gitignore 通过")

    # 测试 2：.env.example 应该通过
    print("  📝 测试 2：.env.example")
    plan2 = "## 计划\n\n### 计划修改文件\n- `.env.example` - 追加环境变量"
    passed2, error2 = validate_first_file_exists(plan2, mock_repo)
    assert passed2 == True, f"❌ .env.example 应该通过，但错误: {error2}"
    print("    ✅ .env.example 通过")

    # 测试 3：requirements.txt 应该失败（暂不支持）
    print("  📝 测试 3：requirements.txt")
    plan3 = "## 计划\n\n### 计划修改文件\n- `requirements.txt` - 追加依赖"
    passed3, error3 = validate_first_file_exists(plan3, mock_repo)
    assert passed3 == False, f"❌ requirements.txt 应该失败，但通过了"
    assert "不在当前支持范围内" in error3, f"❌ 错误信息应该提示'不在当前支持范围内'，但: {error3}"
    print("    ✅ requirements.txt 正确拒绝")

    # 测试 4：config/.gitignore 应该失败（子目录）
    print("  📝 测试 4：config/.gitignore")
    plan4 = "## 计划\n\n### 计划修改文件\n- `config/.gitignore` - 测试"
    passed4, error4 = validate_first_file_exists(plan4, mock_repo)
    assert passed4 == False, f"❌ config/.gitignore 应该失败，但通过了"
    assert "不在当前支持范围内" in error4, f"❌ 错误信息应该提示'不在当前支持范围内'，但: {error4}"
    print("    ✅ config/.gitignore 正确拒绝")

    print("  ✅ validate_first_file_exists() 测试通过\n")


def test_validate_append_content():
    """测试追加内容安全验证"""
    print("🧪 测试 validate_append_content()...")

    # 测试 1：空内容应该拒绝
    print("  📝 测试 1：空内容")
    result1 = validate_append_content(".gitignore", "", "existing content")
    assert result1['valid'] == False, "❌ 空内容应该被拒绝"
    print("    ✅ 空内容正确拒绝")

    # 测试 2：包含敏感信息应该拒绝
    print("  📝 测试 2：敏感信息")
    result2 = validate_append_content(".env.example", "API_KEY=sk-abc123", "existing")
    assert result2['valid'] == False, "❌ 包含 API key 应该被拒绝"
    assert "敏感信息" in result2['reason'], "❌ 错误信息应该提示敏感信息"
    print("    ✅ 敏感信息正确拒绝")

    # 测试 3：正常内容应该通过
    print("  📝 测试 3：正常 .gitignore 内容")
    result3 = validate_append_content(".gitignore", "*.log\n\ntemp/", "existing")
    assert result3['valid'] == True, f"❌ 正常内容应该通过，但: {result3['reason']}"
    print("    ✅ 正常 .gitignore 内容通过")

    # 测试 4：正常 .env.example 内容应该通过
    print("  📝 测试 4：正常 .env.example 内容")
    result4 = validate_append_content(".env.example", "# New variable\nNEW_VAR=example", "existing")
    assert result4['valid'] == True, f"❌ 正常内容应该通过，但: {result4['reason']}"
    print("    ✅ 正常 .env.example 内容通过")

    # 测试 5：内容过长应该拒绝
    print("  📝 测试 5：内容过长")
    long_content = "\n".join([f"line{i}" for i in range(101)])
    result5 = validate_append_content(".gitignore", long_content, "existing")
    assert result5['valid'] == False, "❌ 过长内容应该被拒绝"
    assert "过长" in result5['reason'], "❌ 错误信息应该提示过长"
    print("    ✅ 过长内容正确拒绝")

    # 测试 6：单行过长应该拒绝
    print("  📝 测试 6：单行过长")
    long_line = "a" * 1001
    result6 = validate_append_content(".gitignore", long_line, "existing")
    assert result6['valid'] == False, "❌ 单行过长应该被拒绝"
    assert "过长的行" in result6['reason'], "❌ 错误信息应该提示单行过长"
    print("    ✅ 单行过长正确拒绝")

    print("  ✅ validate_append_content() 测试通过\n")


def test_append_to_file_content():
    """测试安全追加函数"""
    print("🧪 测试 append_to_file_content()...")

    # 测试 1：空文件追加
    print("  📝 测试 1：空文件追加")
    result1 = append_to_file_content("", "new line")
    assert result1 == "new line\n", "❌ 空文件追加结果不正确"
    print("    ✅ 空文件追加正确")

    # 测试 2：正常追加（文件以换行符结尾）
    print("  📝 测试 2：正常追加")
    result2 = append_to_file_content("existing\n", "new line")
    assert result2 == "existing\nnew line\n", "❌ 正常追加结果不正确"
    print("    ✅ 正常追加正确")

    # 测试 3：文件不以换行符结尾
    print("  📝 测试 3：文件不以换行符结尾")
    result3 = append_to_file_content("existing", "new line")
    assert result3 == "existing\nnew line\n", "❌ 追加结果不正确"
    print("    ✅ 不以换行符结尾的追加正确")

    # 测试 4：确保结果以换行符结尾
    print("  📝 测试 4：确保结果以换行符结尾")
    result4 = append_to_file_content("existing\n", "new line")
    assert result4.endswith('\n'), "❌ 结果应该以换行符结尾"
    print("    ✅ 结果以换行符结尾正确")

    print("  ✅ append_to_file_content() 测试通过\n")


if __name__ == "__main__":
    try:
        print("="*60)
        print("🚀 Stage 8.2 本地逻辑测试开始")
        print("="*60 + "\n")

        test_is_supported_append_only_config_file()
        test_function_consistency()
        test_construct_modification_objective()
        test_get_last_n_lines()
        test_validate_first_file_with_config()
        test_validate_append_content()
        test_append_to_file_content()

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
