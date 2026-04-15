#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的本地测试脚本
"""
import os
import sys
from dotenv import load_dotenv

def test_environment():
    """测试环境设置"""
    print("="*60)
    print("环境设置测试")
    print("="*60)

    load_dotenv()
    print("[OK] .env文件已加载")

    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("[ERROR] ZHIPU_API_KEY未找到")
        return False

    print(f"[OK] ZHIPU_API_KEY已找到 (长度: {len(api_key)})")
    return True

def test_imports():
    """测试依赖包"""
    print("\n" + "="*60)
    print("依赖包测试")
    print("="*60)

    try:
        import zhipuai
        print(f"[OK] zhipuai (v{zhipuai.__version__})")
    except ImportError as e:
        print(f"[ERROR] zhipuai导入失败: {e}")
        return False

    try:
        import github
        print("[OK] PyGithub (installed)")
    except ImportError as e:
        print(f"[ERROR] PyGithub导入失败: {e}")
        return False

    return True

def test_zhipu_api():
    """测试智谱API"""
    print("\n" + "="*60)
    print("智谱API测试")
    print("="*60)

    try:
        from zhipuai import ZhipuAI
        api_key = os.getenv('ZHIPU_API_KEY')

        print("[INFO] 连接到智谱AI...")
        client = ZhipuAI(api_key=api_key)

        print("[INFO] 发送测试请求...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=50,
        )

        result = response.choices[0].message.content
        print("[OK] API调用成功")
        # 安全地处理可能包含特殊字符的结果
        try:
            print(f"[INFO] AI回复: {result[:100]}...")
        except UnicodeEncodeError:
            print("[INFO] AI回复: (包含特殊字符，已省略)")
        return True

    except Exception as e:
        print(f"[ERROR] API调用失败: {e}")
        return False

def test_files():
    """测试文件存在性"""
    print("\n" + "="*60)
    print("文件检查")
    print("="*60)

    files_to_check = [
        ("工作流文件", ".github/workflows/claude-issue-handler.yml"),
        ("处理器脚本", ".github/scripts/claude_issue_handler_simple.py"),
    ]

    all_exist = True
    for name, path in files_to_check:
        if os.path.exists(path):
            print(f"[OK] {name}: {path}")
        else:
            print(f"[ERROR] {name}不存在: {path}")
            all_exist = False

    return all_exist

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("智谱AI自动化系统 - 完整测试")
    print("="*60 + "\n")

    tests = [
        ("环境设置", test_environment),
        ("依赖包", test_imports),
        ("智谱API", test_zhipu_api),
        ("文件检查", test_files),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name}测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # 总结
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)

    all_passed = True
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n[SUCCESS] 所有测试通过！")
        print("\n下一步操作:")
        print("1. 验证GitHub Secrets (ZHIPU_API_KEY)")
        print("2. 推送代码到GitHub")
        print("3. 创建带claude-auto标签的Issue")
        print("4. 观察自动化执行")
        return True
    else:
        print("\n[FAIL] 部分测试失败，请修复问题")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
