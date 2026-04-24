---
name: Zhipu Agent 测试
about: 测试 Zhipu Issue Agent 功能
title: '[TEST] Zhipu Agent 测试'
labels: testing
assignees: ''

---

## 测试 Zhipu Issue Agent

这是一个用于测试 Zhipu Issue Agent 的 Issue 模板。

### 如何测试

1. **创建 Issue**: 使用此模板创建一个新 Issue
2. **添加描述**: 在下方描述你想要实现的功能
3. **触发 Agent**: 在评论区输入 `@zhipu`
4. **等待响应**: 1-2 分钟后，Agent 会自动生成执行计划

### 示例问题

你可以填写以下任一示例问题来测试：

#### 示例 1: 添加新功能
```
我想添加一个 API 端点，用于获取课程统计信息。

要求：
- 返回课程总数
- 返回文档总数
- 返回平均每个课程的文档数量
- 使用现有的 Course 模型
```

#### 示例 2: 修复 Bug
```
当前系统在处理中文查询时，搜索结果不太准确。

可能的原因：
- 分词问题
- embedding 模型对中文支持不好
- 查询预处理逻辑问题

期望：
- 改进中文查询的相关性
- 测试几个中文查询案例
```

#### 示例 3: 重构代码
```
`ai_generator.py` 文件中的 `_handle_tool_execution` 方法太长了（100+ 行）。

希望：
- 将其拆分为多个小方法
- 提高可读性和可维护性
- 保持原有功能不变
```

### 你的问题

请在下方描述你的问题：

---

**提示**: 在评论区输入 `@zhipu` 即可触发 Agent 生成执行计划。
