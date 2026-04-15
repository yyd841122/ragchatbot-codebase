#!/usr/bin/env python3
"""
测试智谱AI API连接
"""
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

def test_zhipu_api():
    """测试智谱AI API是否正常工作"""
    print("🧪 测试智谱AI API连接...")
    print("=" * 50)

    # 获取API Key
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("❌ 错误：ZHIPU_API_KEY 环境变量未设置")
        print("\n请确保在项目根目录有 .env 文件，包含：")
        print("ZHIPU_API_KEY=your_api_key_here")
        return False

    print(f"✅ API Key 已加载（长度: {len(api_key)} 字符）")

    try:
        # 初始化客户端
        print("📡 连接到智谱AI...")
        client = ZhipuAI(api_key=api_key)

        # 测试简单的API调用
        print("🤖 发送测试请求...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": "请用一句话介绍你自己"
                }
            ],
            max_tokens=100,
        )

        print("✅ API调用成功！")
        print("=" * 50)
        print("AI 回复：")
        print(response.choices[0].message.content)
        print("=" * 50)

        # 测试较长的请求
        print("\n🧪 测试较长请求（模拟Issue分析）...")
        test_prompt = """你是一个专业的开发者。

# 任务
分析以下简单的Issue：
标题：测试Issue
内容：这是一个测试

请提供简短的分析和建议（不超过100字）。"""

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": test_prompt
                }
            ],
            max_tokens=500,
        )

        print("✅ 长请求测试成功！")
        print("AI 分析：")
        print(response.choices[0].message.content)
        print("=" * 50)

        print("\n🎉 所有测试通过！你的智谱API配置正常。")
        return True

    except Exception as e:
        print(f"❌ API调用失败: {type(e).__name__}: {e}")
        print("\n可能的原因：")
        print("1. API Key 不正确")
        print("2. 网络连接问题")
        print("3. 智谱API服务暂时不可用")
        print("4. API Key 没有足够的额度")
        print("\n请检查：")
        print("- .env 文件中的 ZHIPU_API_KEY 是否正确")
        print("- 网络连接是否正常")
        print("- 智谱AI账户是否有可用额度")
        return False

if __name__ == "__main__":
    success = test_zhipu_api()
    exit(0 if success else 1)
