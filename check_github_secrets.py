#!/usr/bin/env python3
"""
GitHub Secrets检查工具
帮助验证GitHub Secrets是否正确设置
"""
import os
import sys
from dotenv import load_dotenv

def load_env():
    """加载.env文件"""
    load_dotenv()
    print("📁 已加载 .env 文件")

def check_local_env():
    """检查本地环境变量"""
    print("\n🔍 本地环境变量检查:")
    print("="*60)

    zhipu_key = os.getenv('ZHIPU_API_KEY')

    if not zhipu_key:
        print("❌ ZHIPU_API_KEY 未在本地 .env 文件中找到")
        print("\n请在项目根目录创建 .env 文件，包含:")
        print("ZHIPU_API_KEY=your_api_key_here")
        return False

    print(f"✅ ZHIPU_API_KEY 已找到")
    print(f"   长度: {len(zhipu_key)} 字符")
    print(f"   格式: {'*' * 20}...{zhipu_key[-8:]}")

    # 验证格式
    if '.' in zhipu_key:
        print("✅ 格式正确 (包含 . 分隔符)")
    else:
        print("⚠️  格式可能不正确 (缺少 . 分隔符)")

    return True

def test_zhipu_api():
    """测试智谱API连接"""
    print("\n🧪 智谱API连接测试:")
    print("="*60)

    try:
        from zhipuai import ZhipuAI
        print("✅ ZhipuAI 包已导入")
    except ImportError:
        print("❌ ZhipuAI 包未安装")
        print("请运行: pip install zhipuai")
        return False

    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("❌ API Key 未找到")
        return False

    try:
        print("📡 连接到智谱AI...")
        client = ZhipuAI(api_key=api_key)

        print("🤖 测试API调用...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": "你好，请用一句话介绍你自己"}],
            max_tokens=50,
        )

        result = response.choices[0].message.content
        print("✅ API调用成功")
        print(f"📝 AI回复: {result}")

        return True

    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print("\n可能原因:")
        print("1. API Key 错误")
        print("2. 账户余额不足")
        print("3. 网络连接问题")
        return False

def check_github_secrets():
    """检查GitHub Secrets设置指南"""
    print("\n🔧 GitHub Secrets 设置检查:")
    print("="*60)

    print("请确认以下步骤:")
    print("1. 访问 GitHub 仓库 Settings 页面")
    print("2. 进入: Secrets and variables → Actions")
    print("3. 确认有 ZHIPU_API_KEY secret")
    print("4. 值应该与本地 .env 文件中的相同")

    print("\n📋 GitHub CLI 验证命令:")
    print("gh secret list --repo yyd841122/ragchatbot-codebase")

def main():
    """主函数"""
    print("="*60)
    print("🔍 GitHub Secrets 验证工具")
    print("="*60)

    # 加载环境变量
    load_env()

    # 检查本地环境
    if not check_local_env():
        return False

    # 测试API连接
    if not test_zhipu_api():
        return False

    # GitHub设置检查
    check_github_secrets()

    print("\n" + "="*60)
    print("✅ 本地验证通过!")
    print("="*60)
    print("\n下一步:")
    print("1. 确认 GitHub Secrets 已正确设置")
    print("2. 推送代码到 GitHub")
    print("3. 创建带 'claude-auto' 标签的 Issue")
    print("4. 观察 GitHub Actions 执行情况")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
