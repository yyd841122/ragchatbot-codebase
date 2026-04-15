# 前端功能更新：主题切换按钮

## 更新日期
2026-04-15

## 新增功能

### 主题切换按钮
在应用右上角添加了一个可访问的主题切换按钮，允许用户在深色和浅色主题之间切换。

## 实现细节

### 1. HTML 更新 (`frontend/index.html`)

**位置**: `<body>` 标签开始后，`<div class="container">` 之前

**新增元素**:
```html
<button id="themeToggle" class="theme-toggle" aria-label="Toggle theme" title="Toggle theme">
    <span class="theme-toggle-icon">
        <svg class="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg class="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    </span>
</button>
```

**特性**:
- 使用 `aria-label` 提供屏幕阅读器支持
- 添加 `title` 属性提供悬停提示
- 太阳和月亮图标使用 SVG 渲染

### 2. CSS 更新 (`frontend/style.css`)

#### 2.1 主题变量系统

**深色主题（默认）**:
```css
:root {
    --primary-color: #2563eb;
    --background: #0f172a;
    --surface: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: #334155;
    /* ... 其他变量 */
}
```

**浅色主题**:
```css
[data-theme="light"] {
    --background: #f8fafc;
    --surface: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    /* ... 其他变量 */
}
```

#### 2.2 主题过渡动画

为关键元素添加了 0.3 秒的平滑过渡：
```css
body, .container, .sidebar, .chat-main, .chat-container,
.chat-messages, .message-content, .chat-input-container,
#chatInput, .theme-toggle {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
```

#### 2.3 主题切换按钮样式

**位置**: 固定在右上角
- 桌面端: `top: 1.5rem; right: 1.5rem`
- 移动端: `top: 1rem; right: 1rem`

**按钮特性**:
- 圆形按钮（border-radius: 50%）
- 尺寸: 48px（桌面）/ 44px（移动）
- 悬停效果: 放大 1.05 倍，添加阴影
- 点击效果: 缩小 0.95 倍
- Focus 状态: 蓝色光环效果

**图标动画**:
- 深色主题: 显示太阳图标
- 浅色主题: 显示月亮图标
- 切换时旋转 90 度，淡入淡出效果

### 3. JavaScript 更新 (`frontend/script.js`)

#### 3.1 新增函数: `setupThemeToggle()`

**功能**:
1. 检查本地存储中保存的主题偏好，默认为深色主题
2. 为按钮添加点击事件监听器
3. 切换主题时更新 `data-theme` 属性
4. 保存用户偏好到 `localStorage`
5. 添加按钮点击动画（缩放+旋转）
6. 支持键盘导航（Enter 和 Space 键）

**代码位置**: 在 `DOMContentLoaded` 事件监听器中调用

## 用户体验改进

### 视觉效果
- **平滑过渡**: 所有颜色变化都有 0.3 秒的过渡动画
- **图标动画**: 切换时图标旋转并淡入淡出
- **按钮反馈**: 悬停、点击、Focus 状态都有视觉反馈

### 可访问性
- **键盘导航**: 支持 Tab 键选中，Enter/Space 键切换
- **屏幕阅读器**: `aria-label` 提供语义化标签
- **Focus 可见**: 清晰的 Focus 环光效果
- **颜色对比**: 浅色和深色主题都保持良好的对比度

### 持久化
- 使用 `localStorage` 保存用户偏好
- 页面刷新后自动恢复上次的主题选择
- 默认主题为深色（符合原有设计）

## 浏览器兼容性

- 使用标准 CSS 变量（支持所有现代浏览器）
- SVG 图标（支持所有现代浏览器）
- LocalStorage API（支持所有现代浏览器）
- CSS Transitions（支持所有现代浏览器）

## 测试建议

1. **功能测试**:
   - 点击按钮切换主题
   - 刷新页面验证主题保持
   - 使用键盘导航测试

2. **视觉测试**:
   - 验证所有组件在两种主题下都正常显示
   - 检查颜色对比度
   - 测试过渡动画流畅度

3. **响应式测试**:
   - 桌面端按钮位置和大小
   - 移动端按钮位置和大小
   - 不同屏幕尺寸下的表现

## 文件修改清单

1. ✅ `frontend/index.html` - 添加主题切换按钮 HTML
2. ✅ `frontend/style.css` - 添加主题变量和按钮样式
3. ✅ `frontend/script.js` - 添加主题切换逻辑

## 后续优化建议

1. 可以添加系统主题检测（`prefers-color-scheme`）自动切换
2. 可以添加更多主题选项（如高对比度主题）
3. 可以在设置面板中添加主题选择器
4. 可以添加主题切换的快捷键（如 Ctrl/Cmd + Shift + T）
