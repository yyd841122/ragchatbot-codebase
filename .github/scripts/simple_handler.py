import os
import sys

def main():
    # 简单的错误处理
    try:
        print("="*60)
        print("🤖 智谱AI Issue处理器")
        print("="*60)

        # 获取环境变量
        token = os.getenv('GITHUB_TOKEN')
        api_key = os.getenv('ZHIPU_API_KEY')
        issue_num = os.getenv('ISSUE_NUMBER')
        repo_name = os.getenv('REPO')

        # 验证必需的环境变量
        if not all([token, api_key, issue_num, repo_name]):
            print("❌ ERROR: Missing environment variables")
            print(f"GITHUB_TOKEN: {'✅' if token else '❌ MISSING'}")
            print(f"ZHIPU_API_KEY: {'✅' if api_key else '❌ MISSING'}")
            print(f"ISSUE_NUMBER: {'✅' if issue_num else '❌ MISSING'}")
            print(f"REPO: {'✅' if repo_name else '❌ MISSING'}")
            sys.exit(1)

        print(f"✅ Environment variables loaded")
        print(f"📝 Processing Issue #{issue_num} in {repo_name}")

        # 导入依赖
        print("📦 Importing dependencies...")
        try:
            from github import Github
            print("✅ PyGithub imported")
        except ImportError as e:
            print(f"❌ Failed to import PyGithub: {e}")
            sys.exit(1)

        try:
            from zhipuai import ZhipuAI
            print("✅ ZhipuAI imported")
        except ImportError as e:
            print(f"❌ Failed to import ZhipuAI: {e}")
            print("💡 Hint: Check .github/requirements.txt includes zhipuai")
            sys.exit(1)

        # 连接GitHub
        print("🔗 Connecting to GitHub...")
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(int(issue_num))

        print(f"✅ Connected to Issue: {issue.title[:50]}...")

        # 调用智谱AI
        print("🤖 Calling Zhipu AI...")
        client = ZhipuAI(api_key=api_key)

        prompt = f"分析这个GitHub Issue并提供建议：\n标题：{issue.title}\n内容：{issue.body or '无'}"

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        result = response.choices[0].message.content
        print(f"✅ AI response received ({len(result)} characters)")

        # 发表评论
        print("💬 Posting comment to Issue...")
        comment = f"## 🤖 智谱AI分析\n\n{result}\n\n---\n*由智谱AI自动生成*"
        issue.create_comment(comment)

        print("✅ SUCCESS: Analysis completed and comment posted")
        print("="*60)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
