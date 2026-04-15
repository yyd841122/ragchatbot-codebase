# 🚨 故障排除指南

## 问题诊断清单

### 1. 本地验证（必须首先进行）

```bash
# 运行本地检查
uv run python check_github_secrets.py
```

这会验证：
- ✅ 本地 API Key 是否正确
- ✅ 智谱AI服务是否可用
- ✅ 网络连接是否正常

### 2. GitHub Secrets 验证

```bash
# 检查 Secrets 是否设置
gh secret list --repo yyd841122/ragchatbot-codebase

# 应该看到:
# ZHIPU_API_KEY    Updated 2024-01-15 XX:XX:XX
```

### 3. 工作流触发问题

#### 问题：工作流没有自动触发

**解决方案：**

1. **检查标签拼写**
   - 必须是: `claude-auto` (全部小写，带连字符)
   - 不能是: `claude_auto` 或 `Claude-Auto`

2. **手动触发工作流**
   ```
   访问: https://github.com/yyd841122/ragchatbot-codebase/actions
   点击: "Zhipu AI Issue Handler" → "Run workflow"
   输入: Issue 编号
   ```

3. **检查工作流日志**
   ```
   点击具体运行记录 → 展开每个步骤
   查看 "Debug environment" 步骤的输出
   ```

### 4. 常见错误和解决方案

#### 错误：Missing required environment variables

**原因：** GitHub Secrets 未设置

**解决：**
```
1. 访问仓库 Settings
2. Secrets and variables → Actions
3. 添加 ZHIPU_API_KEY
4. 粘贴你的智谱API Key
```

#### 错误：智谱AI调用失败

**原因：** API Key 错误或服务问题

**解决：**
```bash
# 1. 本地测试API
uv run python check_github_secrets.py

# 2. 检查账户余额
访问: https://open.bigmodel.cn/usercenter/balance

# 3. 重新生成API Key
访问: https://open.bigmodel.cn/usercenter/apikeys
```

#### 错误：GitHub连接失败

**原因：** 权限或Token问题

**解决：**
```
1. 检查仓库权限
2. 确认 Issues 和 Actions 已启用
3. 验证 GITHUB_TOKEN 权限
```

#### 错误：发表评论失败

**原因：** Issue 状态或权限问题

**解决：**
```
1. 确认 Issue 未被锁定
2. 检查仓库是否允许评论
3. 验证 Token 的 issues:write 权限
```

### 5. 调试步骤

#### 完整调试流程

```
第1步: 本地验证
├── 运行: uv run python check_github_secrets.py
├── 确认: ✅ 本地API正常
└── 如果失败: 检查 .env 文件和 API Key

第2步: GitHub配置检查
├── 运行: gh secret list --repo yyd841122/ragchatbot-codebase
├── 确认: ZHIPU_API_KEY 已设置
└── 如果未设置: 手动添加 Secret

第3步: 工作流触发测试
├── 创建测试 Issue
├── 添加 claude-auto 标签
└── 观察 Actions 页面

第4步: 日志分析
├── 访问 Actions 页面
├── 点击具体运行记录
├── 展开每个步骤查看详细日志
└── 找到失败的具体步骤

第5步: 修复问题
├── 根据错误信息确定问题
├── 应用对应的解决方案
├── 提交修复到 GitHub
└── 重新测试
```

### 6. 环境变量验证

#### 期望的 GitHub Actions 环境信息

```
=== GitHub Event Debug ===
Event name: issues
Repository: yyd841122/ragchatbot-codebase
Actor: your-username
Issue number: 1
Issue labels: ["claude-auto", "bug"]
Has claude-auto label: true
Workflow dispatch issue: 1
```

### 7. 成功的标志

#### GitHub Actions 全部绿色

```
✅ Checkout repository
✅ Setup Python
✅ Install dependencies
✅ Verify Python packages
✅ Debug environment
✅ Run Zhipu AI Handler
```

#### Issue 中出现 AI 评论

```markdown
## 🤖 智谱AI分析结果

[详细的AI分析和建议...]

---
*由智谱AI自动生成 - Issue自动化处理*
```

### 8. 快速测试命令

```bash
# 本地完整测试
uv run python check_github_secrets.py

# 验证 GitHub Secrets
gh secret list --repo yyd841122/ragchatbot-codebase

# 查看最近的工作流运行
gh run list --repo yyd841122/ragchatbot-codebase

# 监控运行中的工作流
gh run watch --repo yyd841122/ragchatbot-codebase
```

### 9. 获取帮助

如果以上步骤都尝试过仍有问题：

1. **收集日志信息**
   - GitHub Actions 完整日志
   - 本地测试结果
   - 具体错误消息

2. **检查配置文件**
   - `.github/workflows/claude-issue-handler.yml`
   - `.github/scripts/claude_issue_handler_simple.py`

3. **验证环境**
   - Python 版本 (需要 3.13+)
   - 依赖包版本
   - 网络连接状态

---

## 📞 紧急修复清单

如果系统完全不工作，按顺序检查：

```
□ 本地 API 测试通过
□ GitHub Secrets 已设置
□ 工作流文件已推送
□ Issue 有 claude-auto 标签
□ GitHub Actions 已启用
□ 仓库权限设置正确
□ 网络连接正常
```

**最常见的问题：**
1. GitHub Secrets 未设置 (90%的情况)
2. 标签拼写错误
3. API Key 错误或过期
