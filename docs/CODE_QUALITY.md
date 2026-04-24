# 代码质量工具使用指南

本项目配置了以下代码质量工具：

## 已安装的工具

- **Black**: 自动代码格式化工具
- **isort**: 导入语句排序工具
- **Flake8**: 代码风格检查工具
- **Pylint**: 代码质量分析工具（可选）

## 配置文件

- `pyproject.toml` - 包含 Black、isort 和 Pylint 的配置
- `.flake8` - Flake8 配置文件

## 使用方法

### 快捷脚本

#### Windows
```cmd
REM 格式化所有代码
scripts\dev.bat format

REM 运行质量检查
scripts\dev.bat check

REM 运行测试
scripts\dev.bat test

REM 启动开发服务器
scripts\dev.bat serve
```

#### Linux/Mac (Git Bash)
```bash
# 格式化所有代码
bash scripts/dev.sh format

# 运行质量检查
bash scripts/dev.sh check

# 运行测试
bash scripts/dev.sh test

# 启动开发服务器
bash scripts/dev.sh serve
```

### 直接使用 Python 脚本

```bash
# 格式化代码
python scripts/format.py

# 运行质量检查
python scripts/check_quality.py
```

### 手动运行各个工具

```bash
# Black 格式化
uv run black backend/

# Black 检查（不修改文件）
uv run black --check backend/

# isort 排序导入
uv run isort backend/

# isort 检查
uv run isort --check-only backend/

# Flake8 检查
uv run flake8 backend/ --config .flake8

# Pylint 检查
uv run pylint backend/
```

## 代码风格规范

### Black 配置
- 行长度: 100 字符
- 目标 Python 版本: 3.13
- 自动处理引号、空格、换行等格式问题

### isort 配置
- 行长度: 100 字符
- 配置文件: 与 Black 兼容
- 自动分组导入：标准库、第三方库、本地模块

### Flake8 配置
- 行长度: 100 字符
- 忽略的规则:
  - E203, W503: Black 兼容性
  - E402: 允许有条件的导入
  - D1xx, D4xx: 放宽文档字符串要求
  - F401, F811: 允许未使用的导入（类型提示）
  - E722: 允许裸 except

## 集成到开发流程

### 在提交代码前

```bash
# 1. 格式化代码
python scripts/format.py

# 2. 运行质量检查
python scripts/check_quality.py

# 3. 运行测试
cd backend && uv run pytest -v

# 4. 如果所有检查通过，提交代码
git add .
git commit -m "your commit message"
```

### 预提交钩子（可选）

可以使用 Git hooks 自动运行检查：

```bash
# 创建预提交钩子
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "运行代码质量检查..."
python scripts/check_quality.py
if [ $? -ne 0 ]; then
    echo "代码质量检查失败，请修复后再提交"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

## 故障排查

### Black 格式化失败
- 检查文件语法错误
- 确保 `uv sync` 已运行

### Flake8 报错过多
- 查看 `.flake8` 配置
- 可以根据项目需求调整忽略规则

### 导入问题
- 确保 `uv sync` 已安装所有依赖
- 检查虚拟环境是否正确激活

## 最佳实践

1. **定期格式化**: 每次开发完成后运行 `python scripts/format.py`
2. **提交前检查**: 始终在提交前运行 `python scripts/check_quality.py`
3. **IDE 集成**:
   - VS Code: 安装 Python 扩展，启用格式化
   - PyCharm: 内置 Black 和 isort 支持
4. **持续集成**: 在 CI/CD 流程中运行质量检查

## 贡献代码

在提交 Pull Request 前，请确保：
1. 运行 `python scripts/format.py` 格式化代码
2. 运行 `python scripts/check_quality.py` 确保通过所有检查
3. 运行 `cd backend && uv run pytest -v` 确保测试通过