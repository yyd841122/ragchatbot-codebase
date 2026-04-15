#!/usr/bin/env python3
"""
智谱AI Issue处理器 - 健壮版本
处理所有边缘情况和错误
"""
import os
import sys

def log_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def log_step(step_num, title):
    """打印步骤标题"""
    print(f"\n{step_num}. {title}")
    print('-' * 60)

def log_success(msg):
    """打印成功消息"""
    print(f"✅ {msg}")

def log_error(msg):
    """打印错误消息"""
    print(f"❌ {msg}")

def log_info(msg):
    """打印信息"""
    print(f"ℹ️  {msg}")

def check_env_vars():
    """检查环境变量"""
    log_step(1, "环境变量检查")

    env_vars = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
        'REPO_NAME': os.environ.get('REPO_NAME'),
        'ISSUE_NUMBER': os.environ.get('ISSUE_NUMBER'),
        'ZHIPU_API_KEY': os.environ.get('ZHIPU_API_KEY')
    }

    missing = []
    for name, value in env_vars.items():
        if value:
            # 隐藏敏感信息
            if 'KEY' in name or 'TOKEN' in name:
                masked = '*' * 8 + value[-4:] if len(value) > 4 else '****'
                log_info(f"{name}: {masked}")
            else:
                log_info(f"{name}: {value}")
        else:
            log_error(f"{name}: 未设置")
            missing.append(name)

    if missing:
        log_error(f"缺少环境变量: {', '.join(missing)}")
        log_info("请检查GitHub Secrets和工作流配置")
        return False

    log_success("所有环境变量已设置")
    return env_vars

def check_imports():
    """检查依赖包"""
    log_step(2, "依赖包检查")

    packages = {
        'github': 'PyGithub',
        'zhipuai': 'ZhipuAI'
    }

    for module_name, package_name in packages.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            log_success(f"{package_name} (v{version})")
        except ImportError as e:
            log_error(f"{package_name} 导入失败: {e}")
            log_info(f"请运行: pip install {package_name.lower() if package_name != 'PyGithub' else 'PyGithub'}")
            return False

    log_success("所有依赖包已安装")
    return True

def connect_github(env_vars):
    """连接GitHub"""
    log_step(3, "GitHub连接")

    try:
        from github import Github

        log_info("初始化GitHub客户端...")
        g = Github(env_vars['GITHUB_TOKEN'])

        log_info(f"访问仓库: {env_vars['REPO_NAME']}")
        repo = g.get_repo(env_vars['REPO_NAME'])
        log_success(f"已连接到仓库: {repo.full_name}")

        issue_number = int(env_vars['ISSUE_NUMBER'])
        log_info(f"获取Issue #{issue_number}...")
        issue = repo.get_issue(issue_number)

        log_success(f"已获取Issue: {issue.title[:50]}...")
        log_info(f"作者: {issue.user.login}")
        log_info(f"状态: {issue.state}")

        return issue

    except Exception as e:
        log_error(f"GitHub连接失败: {e}")
        log_info("可能原因:")
        log_info("1. GITHUB_TOKEN权限不足")
        log_info("2. 仓库名称错误")
        log_info("3. Issue编号无效")
        return None

def call_zhipu_ai(env_vars, issue):
    """调用智谱AI"""
    log_step(4, "智谱AI分析")

    try:
        from zhipuai import ZhipuAI

        log_info("初始化智谱AI客户端...")
        client = ZhipuAI(api_key=env_vars['ZHIPU_API_KEY'])

        # 构建提示词
        prompt = f"""你是GitHub Issue分析专家。请分析以下Issue：

标题: {issue.title}
作者: {issue.user.login}
内容: {issue.body or '无内容'}

请提供:
1. 问题分析
2. 解决建议
3. 具体步骤

用中文回复，简洁明了，不超过300字。"""

        log_info("调用智谱AI API (glm-4-flash)...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )

        result = response.choices[0].message.content
        log_success(f"AI分析完成 ({len(result)}字符)")
        log_info(f"回复预览: {result[:100]}...")

        return result

    except Exception as e:
        log_error(f"智谱AI调用失败: {e}")
        log_info("可能原因:")
        log_info("1. API Key错误或过期")
        log_info("2. 网络连接问题")
        log_info("3. API配额不足")
        log_info("4. 模型名称错误")
        return None

def post_comment(issue, analysis):
    """发表评论到Issue"""
    log_step(5, "发表评论")

    try:
        comment = f"""## 🤖 智谱AI分析结果

{analysis}

---
*由智谱AI自动生成 - Issue自动化处理*
"""

        log_info("发表评论到GitHub...")
        issue.create_comment(comment)
        log_success("评论已成功发表")
        return True

    except Exception as e:
        log_error(f"发表评论失败: {e}")
        log_info("可能原因:")
        log_info("1. GitHub Token权限不足")
        log_info("2. Issue已关闭或锁定")
        log_info("3. 网络连接问题")
        return False

def main():
    """主函数"""
    try:
        log_section("🤖 智谱AI Issue处理器启动")

        # 1. 检查环境变量
        env_vars = check_env_vars()
        if not env_vars:
            sys.exit(1)

        # 2. 检查依赖包
        if not check_imports():
            sys.exit(1)

        # 3. 连接GitHub
        issue = connect_github(env_vars)
        if not issue:
            sys.exit(1)

        # 4. 调用智谱AI
        analysis = call_zhipu_ai(env_vars, issue)
        if not analysis:
            sys.exit(1)

        # 5. 发表评论
        if not post_comment(issue, analysis):
            sys.exit(1)

        # 完成
        log_section("🎉 处理完成")
        log_success("Issue已成功处理并发表AI分析")
        log_section("")

    except KeyboardInterrupt:
        log_error("用户中断")
        sys.exit(1)
    except Exception as e:
        log_section("❌ 发生错误")
        log_error(f"未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
