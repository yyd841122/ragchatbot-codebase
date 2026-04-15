#!/usr/bin/env python3
"""
简化版本的智谱AI Issue处理器
专注于核心功能，减少可能的错误点
"""
import os
import sys

def main():
    """简化的主函数"""
    try:
        print("=" * 60)
        print("🤖 简化版智谱AI处理器")
        print("=" * 60)

        # 1. 检查环境变量
        print("\n1️⃣ 检查环境变量:")
        required_vars = {
            'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
            'REPO_NAME': os.environ.get('REPO_NAME'),
            'ISSUE_NUMBER': os.environ.get('ISSUE_NUMBER'),
            'ZHIPU_API_KEY': os.environ.get('ZHIPU_API_KEY')
        }

        all_present = True
        for var_name, var_value in required_vars.items():
            if var_value:
                if 'KEY' in var_name or 'TOKEN' in var_name:
                    print(f"   ✅ {var_name}: {'*' * 8}...{var_value[-4:]}")
                else:
                    print(f"   ✅ {var_name}: {var_value}")
            else:
                print(f"   ❌ {var_name}: 缺失")
                all_present = False

        if not all_present:
            print("\n❌ 环境变量不完整，退出")
            sys.exit(1)

        print("\n2️⃣ 尝试导入依赖包:")
        try:
            from github import Github
            print("   ✅ PyGithub 导入成功")
        except ImportError as e:
            print(f"   ❌ PyGithub 导入失败: {e}")
            sys.exit(1)

        try:
            from zhipuai import ZhipuAI
            print("   ✅ ZhipuAI 导入成功")
        except ImportError as e:
            print(f"   ❌ ZhipuAI 导入失败: {e}")
            sys.exit(1)

        print("\n3️⃣ 连接GitHub:")
        try:
            g = Github(required_vars['GITHUB_TOKEN'])
            repo = g.get_repo(required_vars['REPO_NAME'])
            issue_number = int(required_vars['ISSUE_NUMBER'])
            issue = repo.get_issue(issue_number)
            print(f"   ✅ 成功获取 Issue #{issue_number}")
            print(f"   标题: {issue.title}")
            print(f"   作者: {issue.user.login}")
        except Exception as e:
            print(f"   ❌ GitHub连接失败: {e}")
            sys.exit(1)

        print("\n4️⃣ 调用智谱AI:")
        try:
            client = ZhipuAI(api_key=required_vars['ZHIPU_API_KEY'])

            # 简化的提示词
            prompt = f"""请分析以下GitHub Issue并提供建议：

标题：{issue.title}
内容：{issue.body or '无内容'}
作者：{issue.user.login}

请用中文回复，包括：
1. 问题分析
2. 解决建议
3. 需要修改的文件（如果有）

保持回复简洁，不超过200字。"""

            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )

            ai_response = response.choices[0].message.content
            print(f"   ✅ AI回复成功（{len(ai_response)}字符）")

        except Exception as e:
            print(f"   ❌ 智谱AI调用失败: {e}")
            print(f"   可能原因：")
            print(f"   1. API Key错误")
            print(f"   2. 网络连接问题")
            print(f"   3. API配额不足")
            sys.exit(1)

        print("\n5️⃣ 发表评论到Issue:")
        try:
            comment = f"""## 🤖 智谱AI 分析

{ai_response}

---
*由智谱AI自动生成*
"""
            issue.create_comment(comment)
            print(f"   ✅ 评论已发表")
        except Exception as e:
            print(f"   ❌ 发表评论失败: {e}")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("🎉 处理完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
