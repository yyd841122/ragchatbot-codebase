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
    extract_explicit_append_content,
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

    # 测试 2：.env.example 中包含正常变量名应该通过（修复误杀）
    print("  📝 测试 2：.env.example 正常变量名（API_KEY）")
    result2 = validate_append_content(".env.example", "API_KEY=example_value", "existing")
    assert result2['valid'] == True, f"❌ 正常变量名应该通过，但: {result2['reason']}"
    print("    ✅ 正常变量名通过")

    # 测试 3：.env.example 中包含真实密钥模式应该拒绝
    print("  📝 测试 3：.env.example 真实密钥（sk-）")
    result3 = validate_append_content(".env.example", "API_KEY=sk-abc123", "existing")
    assert result3['valid'] == False, "❌ 包含真实密钥应该被拒绝"
    assert "真实密钥" in result3['reason'], "❌ 错误信息应该提示真实密钥"
    print("    ✅ 真实密钥正确拒绝")

    # 测试 4：.gitignore 中包含敏感信息应该拒绝
    print("  📝 测试 4：.gitignore 包含敏感词")
    result4 = validate_append_content(".gitignore", "secret_file.txt", "existing")
    assert result4['valid'] == False, "❌ .gitignore 包含敏感词应该被拒绝"
    assert "敏感信息" in result4['reason'], "❌ 错误信息应该提示敏感信息"
    print("    ✅ .gitignore 敏感词正确拒绝")

    # 测试 5：正常 .gitignore 内容应该通过
    print("  📝 测试 5：正常 .gitignore 内容")
    result5 = validate_append_content(".gitignore", "*.log\n\n# Temporary files\ntemp/\n*.tmp", "existing")
    assert result5['valid'] == True, f"❌ 正常 .gitignore 内容应该通过，但: {result5['reason']}"
    print("    ✅ 正常 .gitignore 内容通过")

    # 测试 6：正常 .env.example 内容应该通过
    print("  📝 测试 6：正常 .env.example 内容")
    result6 = validate_append_content(".env.example", "# New variables\nAPI_KEY=example_value\nSECRET_KEY=changeme", "existing")
    assert result6['valid'] == True, f"❌ 正常 .env.example 内容应该通过，但: {result6['reason']}"
    print("    ✅ 正常 .env.example 内容通过")

    # 测试 7：内容过长应该拒绝
    print("  📝 测试 7：内容过长")
    long_content = "\n".join([f"line{i}" for i in range(101)])
    result7 = validate_append_content(".gitignore", long_content, "existing")
    assert result7['valid'] == False, "❌ 过长内容应该被拒绝"
    assert "过长" in result7['reason'], "❌ 错误信息应该提示过长"
    print("    ✅ 过长内容正确拒绝")

    # 测试 8：单行过长应该拒绝
    print("  📝 测试 8：单行过长")
    long_line = "a" * 1001
    result8 = validate_append_content(".gitignore", long_line, "existing")
    assert result8['valid'] == False, "❌ 单行过长应该被拒绝"
    assert "过长的行" in result8['reason'], "❌ 错误信息应该提示单行过长"
    print("    ✅ 单行过长正确拒绝")

    # 测试 9：.gitignore 包含环境变量格式应该拒绝（格式检查）
    print("  📝 测试 9：.gitignore 包含环境变量格式")
    result9 = validate_append_content(".gitignore", "CONFIG=value", "existing")
    assert result9['valid'] == False, "❌ .gitignore 包含环境变量格式应该被拒绝"
    assert "格式错误" in result9['reason'], "❌ 错误信息应该提示格式错误"
    print("    ✅ .gitignore 环境变量格式正确拒绝")

    # 测试 10：.env.example 不包含 "=" 应该拒绝（格式检查）
    print("  📝 测试 10：.env.example 不包含等号")
    result10 = validate_append_content(".env.example", "just_a_word", "existing")
    assert result10['valid'] == False, "❌ .env.example 不包含等号应该被拒绝"
    assert "格式错误" in result10['reason'], "❌ 错误信息应该提示格式错误"
    print("    ✅ .env.example 不包含等号正确拒绝")

    # 测试 11：.env.example 安全占位符应该允许
    print("  📝 测试 11：.env.example 安全占位符")
    result11 = validate_append_content(
        ".env.example",
        "OPENAI_API_KEY=your_openai_api_key_here\nZHIPU_API_KEY=your_zhipu_api_key_here\nGITHUB_TOKEN=your_github_token_here",
        "existing"
    )
    assert result11['valid'] == True, f"❌ 安全占位符应该通过，但: {result11['reason']}"
    print("    ✅ 安全占位符通过")

    # 测试 12：.env.example GitHub token 应该拒绝
    print("  📝 测试 12：.env.example GitHub token (ghp_)")
    result12 = validate_append_content(".env.example", "GITHUB_TOKEN=ghp_abc123", "existing")
    assert result12['valid'] == False, "❌ GitHub token (ghp_) 应该被拒绝"
    assert "真实密钥" in result12['reason'], "❌ 错误信息应该提示真实密钥"
    print("    ✅ GitHub token (ghp_) 正确拒绝")

    # 测试 13：.env.example GitHub token (github_pat_) 应该拒绝
    print("  📝 测试 13：.env.example GitHub token (github_pat_)")
    result13 = validate_append_content(".env.example", "GITHUB_TOKEN=github_pat_abc123", "existing")
    assert result13['valid'] == False, "❌ GitHub token (github_pat_) 应该被拒绝"
    assert "真实密钥" in result13['reason'], "❌ 错误信息应该提示真实密钥"
    print("    ✅ GitHub token (github_pat_) 正确拒绝")

    # 测试 14：.env.example Google API key 应该拒绝
    print("  📝 测试 14：.env.example Google API key (AIza)")
    result14 = validate_append_content(".env.example", "GOOGLE_API_KEY=AIzaabc123", "existing")
    assert result14['valid'] == False, "❌ Google API key (AIza) 应该被拒绝"
    assert "真实密钥" in result14['reason'], "❌ 错误信息应该提示真实密钥"
    print("    ✅ Google API key (AIza) 正确拒绝")

    # 测试 15：.env.example 非法变量名格式（小写开头）应该拒绝
    print("  📝 测试 15：.env.example 非法变量名（小写开头）")
    result15 = validate_append_content(".env.example", "openai_key=value", "existing")
    assert result15['valid'] == False, "❌ 非法变量名（小写开头）应该被拒绝"
    assert "大写字母开头" in result15['reason'], "❌ 错误信息应该提示大写字母开头"
    print("    ✅ 非法变量名正确拒绝")

    # 测试 16：.env.example 非法变量名格式（包含特殊字符）应该拒绝
    print("  📝 测试 16：.env.example 非法变量名（包含 -）")
    result16 = validate_append_content(".env.example", "OpenAI-Key=value", "existing")
    assert result16['valid'] == False, "❌ 非法变量名（包含 -）应该被拒绝"
    assert "非法字符" in result16['reason'], "❌ 错误信息应该提示非法字符"
    print("    ✅ 非法变量名正确拒绝")

    # 测试 17：.gitignore 重复规则应该拒绝
    print("  📝 测试 17：.gitignore 重复规则")
    existing_gitignore = "*.log\n*.tmp\n"
    result17 = validate_append_content(".gitignore", "*.log", existing_gitignore)
    assert result17['valid'] == False, "❌ .gitignore 重复规则应该被拒绝"
    assert "重复" in result17['reason'], "❌ 错误信息应该提示重复"
    print("    ✅ .gitignore 重复规则正确拒绝")

    # 测试 18：.gitignore 正常规则应该允许
    print("  📝 测试 18：.gitignore 正常规则")
    existing_gitignore = "*.log\n*.tmp\n"
    result18 = validate_append_content(".gitignore", "*.bak", existing_gitignore)
    assert result18['valid'] == True, f"❌ .gitignore 正常规则应该通过，但: {result18['reason']}"
    print("    ✅ .gitignore 正常规则通过")

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


def test_extract_explicit_append_content():
    """测试显式内容提取函数"""
    print("🧪 测试 extract_explicit_append_content()...")

    # 测试 1：从 Issue body 中提取 .gitignore 代码块（优先级最高）
    print("  📝 测试 1：Issue body 中的 .gitignore 代码块（优先级最高）")
    issue_body_1 = """
请追加以下忽略规则：
```gitignore
*.stage82.log
*.temp
```
"""
    plan_1 = "## 计划\n\n### 计划修改文件\n- `.gitignore` - 追加忽略规则"
    result1 = extract_explicit_append_content(issue_body_1, plan_1, ".gitignore")
    assert result1['found'] == True, "❌ 应该找到代码块"
    assert result1['source'] == 'issue_body_code_block', "❌ 应该是 issue_body_code_block"
    assert "*.stage82.log" in result1['content'], "❌ 应该包含 *.stage82.log"
    print("    ✅ Issue body .gitignore 代码块正确提取")

    # 测试 2：从 Stage 1 计划中提取 .env.example 代码块（次优先级）
    print("  📝 测试 2：Stage 1 计划中的 .env.example 代码块（次优先级）")
    issue_body_2 = "请追加环境变量"
    plan_2 = """
## 计划

### 计划修改文件
- `.env.example` - 追加环境变量

### 执行内容
```env
NEW_VARIABLE=example_value
ANOTHER_VAR=another_value
```
"""
    result2 = extract_explicit_append_content(issue_body_2, plan_2, ".env.example")
    assert result2['found'] == True, "❌ 应该找到代码块"
    assert result2['source'] == 'plan_code_block', "❌ 应该是 plan_code_block"
    assert "NEW_VARIABLE=example_value" in result2['content'], "❌ 应该包含新变量"
    print("    ✅ Stage 1 计划 .env.example 代码块正确提取")

    # 测试 3：通用代码块提取（无语言标记）
    print("  📝 测试 3：通用代码块提取（无语言标记）")
    issue_body_3 = """
请在 .gitignore 中追加：
```
*.log
*.tmp
temp/
```
"""
    plan_3 = "## 计划\n\n### 计划修改文件\n- `.gitignore` - 追加忽略规则"
    result3 = extract_explicit_append_content(issue_body_3, plan_3, ".gitignore")
    assert result3['found'] == True, "❌ 应该找到代码块"
    assert result3['source'] == 'issue_body_generic_block', "❌ 应该是 issue_body_generic_block"
    assert "*.log" in result3['content'], "❌ 应该包含 *.log"
    print("    ✅ 通用代码块正确提取")

    # 测试 4：多个代码块时选择第一个匹配的
    print("  📝 测试 4：多个代码块时选择第一个匹配的")
    issue_body_4 = """
第一个代码块：
```python
print("ignore this")
```

第二个代码块：
```gitignore
*.first
*.second
```

第三个代码块：
```gitignore
*.third
```
"""
    plan_4 = "## 计划\n\n### 计划修改文件\n- `.gitignore` - 追加忽略规则"
    result4 = extract_explicit_append_content(issue_body_4, plan_4, ".gitignore")
    assert result4['found'] == True, "❌ 应该找到代码块"
    assert "*.first" in result4['content'], "❌ 应该选择第一个匹配的代码块"
    assert "*.third" not in result4['content'], "❌ 不应该包含第三个代码块"
    print("    ✅ 多个代码块正确选择第一个")

    # 测试 5：无代码块时返回 not found
    print("  📝 测试 5：无代码块时返回 not found")
    issue_body_5 = "请在 .gitignore 中追加 *.log 文件"
    plan_5 = "## 计划\n\n### 计划修改文件\n- `.gitignore` - 追加 *.log"
    result5 = extract_explicit_append_content(issue_body_5, plan_5, ".gitignore")
    assert result5['found'] == False, "❌ 无代码块时应该返回 not found"
    assert result5['content'] == "", "❌ 内容应该为空"
    assert result5['source'] is None, "❌ 来源应该为 None"
    print("    ✅ 无代码块时正确返回 not found")

    # 测试 6：Issue body 空时从 Stage 1 计划提取
    print("  📝 测试 6：Issue body 空时从 Stage 1 计划提取")
    issue_body_6 = ""
    plan_6 = """
## 计划

### 计划修改文件
- `.env.example` - 追加环境变量

### 追加内容
```env
FALLBACK_VAR=fallback_value
```
"""
    result6 = extract_explicit_append_content(issue_body_6, plan_6, ".env.example")
    assert result6['found'] == True, "❌ 应该从 Stage 1 计划找到代码块"
    assert result6['source'] == 'plan_code_block', "❌ 应该是 plan_code_block"
    assert "FALLBACK_VAR=fallback_value" in result6['content'], "❌ 应该包含回退变量"
    print("    ✅ 从 Stage 1 计划正确提取")

    # 测试 7：优先级验证（Issue body 优先于 Stage 1 计划）
    print("  📝 测试 7：优先级验证（Issue body 优先于 Stage 1 计划）")
    issue_body_7 = """
```gitignore
*.issue_body
```
"""
    plan_7 = """
## 计划

### 计划修改文件
- `.gitignore` - 追加忽略规则

### 追加内容
```gitignore
*.plan_content
```
"""
    result7 = extract_explicit_append_content(issue_body_7, plan_7, ".gitignore")
    assert result7['found'] == True, "❌ 应该找到代码块"
    assert result7['source'] == 'issue_body_code_block', "❌ Issue body 应该优先于 Stage 1 计划"
    assert "*.issue_body" in result7['content'], "❌ 应该使用 Issue body 的内容"
    assert "*.plan_content" not in result7['content'], "❌ 不应该使用 Stage 1 计划的内容"
    print("    ✅ 优先级正确验证")

    # 测试 8：existing_plan 为空字符串时不会报错（bugfix 验证）
    print("  📝 测试 8：existing_plan 为空字符串时不会报错")
    issue_body_8 = "请在 .gitignore 中追加 *.log"
    plan_8 = ""  # 空 existing_plan
    result8 = extract_explicit_append_content(issue_body_8, plan_8, ".gitignore")
    # 空 existing_plan 应该不报错，只是找不到代码块
    assert result8['found'] == False, "❌ 空 existing_plan 应该返回 not found"
    assert result8['content'] == "", "❌ 内容应该为空"
    assert result8['source'] is None, "❌ 来源应该为 None"
    print("    ✅ 空 existing_plan 不报错")

    print("  ✅ extract_explicit_append_content() 测试通过\n")


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
        test_extract_explicit_append_content()

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
