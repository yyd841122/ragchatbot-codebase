# 用户查询完整流程图

## 1. 端到端主流程图

```mermaid
flowchart TD
    Start([用户输入问题]) --> UI_GetValue[获取输入框内容<br/>chatInput.value]
    UI_GetValue --> UI_Check{内容为空?}
    UI_Check -->|是| End1([结束])
    UI_Check -->|否| UI_Disable[禁用输入和按钮<br/>显示加载动画]

    UI_Disable --> UI_AddMsg[添加用户消息到界面]
    UI_AddMsg --> Fetch[发送HTTP POST请求<br/>/api/query]

    Fetch -->|Request| Backend[FastAPI后端接收]
    Backend --> Validate[Pydantic参数验证<br/>QueryRequest]
    Validate --> Session_Check{session_id存在?}

    Session_Check -->|否| Create_Session[创建新会话<br/>session_manager.create_session]
    Session_Check -->|是| RAG_Query
    Create_Session --> RAG_Query[RAG系统处理<br/>rag_system.query]

    RAG_Query --> Build_Prompt[构建提示词<br/>Answer about course materials]
    Build_Prompt --> Get_History[获取对话历史<br/>session_manager.get_history]

    Get_History --> AI_Call_1[调用智谱AI<br/>第1次:决策阶段]
    AI_Call_1 --> Zhipu_API_1[智谱API处理<br/>分析问题类型]

    Zhipu_API_1 --> AI_Decision{需要搜索?}
    AI_Decision -->|否<br/>通用知识| Direct_Response[AI直接回答<br/>response.content]
    AI_Decision -->|是<br/>课程相关| Tool_Execute[执行工具调用<br/>tool_manager.execute_tool]

    Tool_Execute --> CourseSearch[课程搜索工具<br/>CourseSearchTool.execute]
    CourseSearch --> Vector_Search[向量存储搜索<br/>VectorStore.search]

    Vector_Search --> ChromaDB[ChromaDB查询<br/>语义相似度计算]
    ChromaDB --> Search_Results[返回搜索结果<br/>SearchResults]

    Search_Results --> Format_Results[格式化结果<br/>添加上下文前缀]
    Format_Results --> Track_Sources[记录来源信息<br/>last_sources]

    Track_Sources --> AI_Call_2[调用智谱AI<br/>第2次:生成回答]
    AI_Call_2 --> Zhipu_API_2[智谱API处理<br/>综合搜索结果生成回答]

    Zhipu_API_2 --> Final_Response[获取最终回答<br/>response.content]
    Direct_Response --> Extract_Sources
    Final_Response --> Extract_Sources[提取来源列表<br/>tool_manager.get_last_sources]

    Extract_Sources --> Save_History[保存对话历史<br/>session_manager.add_exchange]
    Save_History --> Build_Response[构建响应对象<br/>QueryResponse]

    Build_Response --> Serialize[序列化为JSON<br/>FastAPI自动处理]
    Serialize --> |Response| HTTP_Response[HTTP 200 OK]

    HTTP_Response --> Fetch_Receive[前端接收响应<br/>response.json]
    Fetch_Receive --> Update_Session[更新会话ID<br/>currentSessionId]

    Update_Session --> Remove_Loading[移除加载动画]
    Remove_Loading --> Parse_Markdown[解析Markdown<br/>marked.parse]

    Parse_Markdown --> Build_HTML[构建消息HTML<br/>添加来源列表]
    Build_HTML --> Render_DOM[渲染到页面<br/>插入DOM]

    Render_DOM --> Restore_State[恢复UI状态<br/>启用输入和按钮]
    Restore_State --> End2([完成✅])

    style Start fill:#e1f5e1
    style End2 fill:#e1f5e1
    style End1 fill:#ffe1e1
    style Fetch fill:#ffe1b8
    style Backend fill:#b8d4ff
    style AI_Call_1 fill:#e1b8ff
    style AI_Call_2 fill:#e1b8ff
    style ChromaDB fill:#ffb8e1
    style Zhipu_API_1 fill:#e1b8ff
    style Zhipu_API_2 fill:#e1b8ff
```

---

## 2. 前端交互详细流程

```mermaid
sequenceDiagram
    actor User as 用户
    participant UI as 前端界面
    participant JS as script.js
    participant API as Fetch API

    User->>UI: 输入问题并点击发送
    UI->>JS: 触发 click 事件
    JS->>JS: sendMessage()
    JS->>JS: 获取输入内容并验证
    JS->>UI: 清空输入框
    JS->>UI: 禁用输入和按钮
    JS->>UI: 添加用户消息到界面
    JS->>UI: 显示加载动画

    JS->>API: fetch('/api/query', POST)
    Note over API: 发送请求到后端

    API-->>JS: 返回 JSON 响应
    JS->>JS: 解析响应数据
    JS->>JS: 更新 session_id
    JS->>UI: 移除加载动画
    JS->>JS: marked.parse(answer)
    JS->>UI: 渲染回答和来源
    JS->>UI: 恢复输入状态
    UI->>User: 显示最终回答
```

---

## 3. 后端处理详细流程

```mermaid
flowchart TD
    subgraph Frontend ["前端层"]
        A1[用户输入] --> A2[sendMessage]
        A2 --> A3[fetch POST /api/query]
    end

    subgraph Backend ["后端层"]
        B1[FastAPI路由] --> B2[query_documents]
        B2 --> B3[参数验证 QueryRequest]
        B3 --> B4{session_id?}
        B4 -->|否| B5[创建会话]
        B4 -->|是| B6[RAGSystem.query]
        B5 --> B6
    end

    subgraph RAG ["RAG系统层"]
        C1[RAGSystem] --> C2[构建提示词]
        C2 --> C3[获取历史记录]
        C3 --> C4[AI生成器]
    end

    subgraph AI ["AI决策层"]
        D1[AIGenerator] --> D2[第1次智谱API调用]
        D2 --> D3{需要搜索?}
        D3 -->|否| D4[直接回答]
        D3 -->|是| D5[工具执行]
    end

    subgraph Search ["搜索层"]
        E1[ToolManager] --> E2[CourseSearchTool]
        E2 --> E3[VectorStore]
        E3 --> E4[ChromaDB]
        E4 --> E5[向量相似度计算]
        E5 --> E6[返回Top-K结果]
    end

    subgraph Response ["响应层"]
        F1[格式化搜索结果] --> F2[第2次智谱API调用]
        F2 --> F3[生成最终回答]
        F3 --> F4[提取来源]
        F4 --> F5[保存历史]
        F5 --> F6[构建QueryResponse]
    end

    subgraph Return ["返回层"]
        G1[序列化JSON] --> G2[HTTP 200 OK]
        G2 --> G3[前端接收]
        G3 --> G4[渲染UI]
    end

    A3 -.->|HTTP| B1
    B6 -.->|调用| C1
    C4 -.->|调用| D1
    D5 -.->|执行| E1
    E6 -.->|返回| F1
    F6 -.->|HTTP响应| G1
```

---

## 4. AI工具调用决策流程

```mermaid
flowchart TD
    Start([用户问题输入]) --> System_Prompt[应用系统提示词<br/>You are an AI assistant...]
    System_Prompt --> Add_History{有对话历史?}
    Add_History -->|是| Append_History[追加历史记录<br/>Previous conversation]
    Add_History -->|否| Build_Messages
    Append_History --> Build_Messages[构建消息数组<br/>messages]

    Build_Messages --> Add_Tools[添加工具定义<br/>tools: search_course_content]
    Add_Tools --> API_Call_1[调用智谱API<br/>第1次]

    API_Call_1 --> Zhipu_Analyze[智谱AI分析<br/>问题类型判断]
    Zhipu_Analyze --> Check_Type{问题类型?}

    Check_Type -->|通用知识<br/>什么是Python?| Direct_Path[直接生成回答路径]
    Check_Type -->|课程相关<br/>MCP课程讲了什么?| Tool_Path[工具调用路径]

    Direct_Path --> Direct_Answer[AI基于训练数据回答]
    Direct_Answer --> Return_Answer[返回回答内容]

    Tool_Path --> Tool_Decision[AI决策使用工具]
    Tool_Decision --> Build_Tool_Call[构建工具调用<br/>search_course_content]
    Build_Tool_Call --> Extract_Params[提取参数<br/>query, course_name, lesson_number]
    Extract_Params --> Execute_Tool[执行工具]

    Execute_Tool --> Vector_Search[向量搜索<br/>ChromaDB]
    Vector_Search --> Search_Results[返回搜索结果<br/>documents + metadata]
    Search_Results --> Format_Result[格式化为字符串<br/>添加上下文]
    Format_Result --> Build_Tool_Result[构建工具结果消息<br/>role: tool]

    Build_Tool_Result --> API_Call_2[调用智谱API<br/>第2次]
    API_Call_2 --> Generate_Answer[综合搜索结果<br/>生成最终回答]
    Generate_Answer --> Return_Answer

    Return_Answer --> End([返回给RAG系统])

    style Check_Type fill:#ffe1b8
    style API_Call_1 fill:#e1b8ff
    style API_Call_2 fill:#e1b8ff
    style Vector_Search fill:#ffb8e1
    style Direct_Path fill:#e1f5e1
    style Tool_Path fill:#e1f5e1
```

---

## 5. 向量搜索详细流程

```mermaid
flowchart TD
    Start([搜索请求<br/>search_course_content]) --> Parse_Params[解析参数<br/>query, course_name, lesson_number]

    Parse_Params --> Check_Course{有course_name?}
    Check_Course -->|是| Resolve_Course[解析课程名<br/>_resolve_course_name]
    Check_Course -->|否| Build_Filter

    Resolve_Course --> Catalog_Search[搜索course_catalog<br/>模糊匹配]
    Catalog_Search --> Found_Course{找到匹配?}
    Found_Course -->|否| Return_Error[返回错误<br/>No course found]
    Found_Course -->|是| Get_Title[获取精确课程标题<br/>course_title]
    Get_Title --> Build_Filter

    Build_Filter[构建过滤器<br/>_build_filter] --> Check_Lesson{有lesson_number?}
    Check_Lesson -->|有| Combined_Filter[组合过滤器<br/>$and: course_title + lesson_number]
    Check_Lesson -->|无| Single_Filter[单一过滤器<br/>course_title or None]

    Combined_Filter --> Chroma_Query
    Single_Filter --> Chroma_Query[ChromaDB查询<br/>course_content.query]

    Chroma_Query --> Encode_Query[向量化查询<br/>SentenceTransformer]
    Encode_Query --> Calc_Similarity[计算相似度<br/>Cosine Similarity]
    Calc_Similarity --> Apply_Filter[应用元数据过滤<br/>where: filter_dict]
    Apply_Filter --> Top_K[返回Top-K结果<br/>默认K=5]

    Top_K --> Build_Results[构建SearchResults<br/>documents + metadata + distances]
    Build_Results --> Return_Results[返回给搜索工具]

    Return_Results --> Format[格式化结果<br/>_format_results]
    Format --> Add_Context[添加上下文前缀<br/>[Course - Lesson X]]
    Add_Context --> Track_Sources[记录来源<br/>last_sources]
    Track_Sources --> Return_Formatted[返回格式化字符串]

    Return_Formatted --> End([返回给AI])

    style Resolve_Course fill:#b8d4ff
    style Chroma_Query fill:#ffb8e1
    style Encode_Query fill:#e1b8ff
    style Calc_Similarity fill:#ffe1b8
```

---

## 6. 数据结构流转图

```mermaid
graph LR
    subgraph Input ["输入数据"]
        A1["用户输入<br/>'什么是RAG?'"]
        A2["SessionID<br/>null or 'session_1'"]
    end

    subgraph Transform ["数据转换"]
        B1["QueryRequest<br/>{query, session_id}"]
        B2["Prompt<br/>'Answer about...'"]
        B3["Messages<br/>[{role, content}]"]
    end

    subgraph Process ["处理过程"]
        C1["智谱API响应<br/>{tool_calls}"]
        C2["工具参数<br/>{query, course_name}"]
        C3["ChromaDB结果<br/>{documents, metadata}"]
        C4["格式化结果<br/>'[Course - Lesson]'"]
    end

    subgraph Output ["输出数据"]
        D1["AI回答<br/>'RAG是...'"]
        D2["来源列表<br/>['MCP - Lesson 2']"]
        D3["QueryResponse<br/>{answer, sources, session_id}"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> B3

    B3 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4

    C4 --> D1
    C4 --> D2
    D1 --> D3
    D2 --> D3

    style Input fill:#e1f5e1
    style Transform fill:#ffe1b8
    style Process fill:#b8d4ff
    style Output fill:#e1b8ff
```

---

## 7. 异常处理流程

```mermaid
flowchart TD
    Start([请求开始]) --> Try_Block[try-catch块]

    Try_Block --> Frontend_Err{前端错误?}
    Frontend_Err -->|fetch失败| Err_Network[网络错误<br/>Error: Query failed]
    Frontend_Err -->|JSON解析失败| Err_Parse[解析错误<br/>Error: ...]
    Frontend_Err -->|否| Backend_Err

    Err_Network --> Show_Err_UI[显示错误消息<br/>addMessage]
    Err_Parse --> Show_Err_UI
    Show_Err_UI --> Restore_UI[恢复UI状态]

    Backend_Err{后端错误?}
    Backend_Err -->|参数验证失败| Err_Validate[Pydantic ValidationError]
    Backend_Err -->|会话错误| Err_Session[Session not found]
    Backend_Err -->|RAG错误| Err_RAG[RAG system error]
    Backend_Err -->|搜索错误| Err_Search[Search error]
    Backend_Err -->|否| Success

    Err_Validate --> HTTP_500[HTTPException 500]
    Err_Session --> HTTP_500
    Err_RAG --> HTTP_500
    Err_Search --> Return_NoData[返回空结果<br/>No relevant content]

    HTTP_500 --> Err_Response[错误响应JSON]
    Err_Response --> Show_Err_UI
    Return_NoData --> AI_Handle[AI处理空结果<br/>说明没有找到]

    Success --> Normal_Flow[正常流程]
    Normal_Flow --> End([成功完成])
    Restore_UI --> End
    AI_Handle --> End

    style Err_Network fill:#ffe1e1
    style Err_Validate fill:#ffe1e1
    style Err_Session fill:#ffe1e1
    style Err_RAG fill:#ffe1e1
    style Err_Search fill:#ffe1e1
    style Show_Err_UI fill:#ffe1e1
    style Success fill:#e1f5e1
```

---

## 8. 时序图：完整交互流程

```mermaid
sequenceDiagram
    participant U as 👤 用户
    participant F as 🌐 前端
    participant B as ⚙️ FastAPI
    participant R as 🔄 RAG系统
    participant A as 🤖 智谱AI
    participant T as 🔧 工具管理
    participant V as 📊 向量存储
    participant C as 💾 ChromaDB

    U->>F: 输入问题并点击发送
    F->>F: sendMessage()
    F->>B: POST /api/query {query, session_id}

    B->>B: 参数验证
    B->>R: rag_system.query()

    R->>R: 构建提示词
    R->>R: 获取对话历史

    R->>A: 第1次调用 (决策)
    A->>A: 分析问题类型

    alt 需要搜索
        A->>R: 返回 tool_calls
        R->>T: execute_tool()

        T->>V: store.search()
        V->>C: 向量查询
        C->>V: 返回相似结果
        V->>T: 返回SearchResults

        T->>T: 格式化结果
        T->>R: 返回格式化字符串

        R->>A: 第2次调用 (生成回答)
        A->>R: 返回最终回答
    else 直接回答
        A->>R: 直接返回回答
    end

    R->>R: 提取来源
    R->>R: 保存对话历史

    R->>B: 返回 (response, sources)
    B->>B: 构建QueryResponse
    B->>F: HTTP 200 OK {answer, sources, session_id}

    F->>F: 解析JSON
    F->>F: marked.parse()
    F->>U: 显示回答和来源
```

---

## 9. 状态流转图

```mermaid
stateDiagram-v2
    [*] --> Idle: 页面加载完成

    Idle --> Sending: 用户点击发送
    Sending --> Loading: 请求已发送

    Loading --> Processing: 后端处理中
    Processing --> AI_Decision: AI决策阶段

    AI_Decision --> Direct: 通用知识
    AI_Decision --> Searching: 需要搜索

    Searching --> VectorSearch: 向量搜索
    VectorSearch --> Formatting: 格式化结果

    Formatting --> Generating: AI生成回答
    Direct --> Generating: 直接回答

    Generating --> Saving: 保存历史
    Saving --> Returning: 返回响应

    Returning --> Rendering: 渲染UI
    Rendering --> Idle: 恢复初始状态

    Loading --> Error: 请求失败
    Processing --> Error: 处理异常
    Searching --> Error: 搜索失败
    Error --> Idle: 显示错误消息

    note right of Idle
        UI状态:
        - 输入框: 启用
        - 按钮: 启用
        - session_id: 已保存
    end note

    note right of Loading
        UI状态:
        - 输入框: 禁用
        - 按钮: 禁用
        - 显示加载动画
    end note

    note right of Rendering
        UI状态:
        - 显示回答
        - 显示来源列表
        - 滚动到底部
    end note
```

---

## 10. 架构层次图

```mermaid
graph TB
    subgraph Presentation ["表示层"]
        A1[HTML界面]
        A2[CSS样式]
        A3[JavaScript逻辑]
    end

    subgraph API ["API层"]
        B1[FastAPI路由]
        B2[请求验证]
        B3[响应序列化]
    end

    subgraph Business ["业务逻辑层"]
        C1[RAG系统协调器]
        C2[会话管理器]
        C3[提示词构建]
    end

    subgraph Service ["服务层"]
        D1[AI生成器]
        D2[工具管理器]
        D3[文档处理器]
    end

    subgraph Data ["数据层"]
        E1[向量存储]
        E2[ChromaDB]
        E3[智谱AI API]
    end

    A3 -->|HTTP| B1
    B1 --> B2
    B2 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> D1
    D1 --> D2
    D2 --> D3
    D1 --> E1
    E1 --> E2
    D1 --> E3

    style Presentation fill:#e1f5e1
    style API fill:#ffe1b8
    style Business fill:#b8d4ff
    style Service fill:#e1b8ff
    style Data fill:#ffb8e1
```

---

## 使用说明

这些流程图可以用以下方式查看：

1. **GitHub/GitLab**: 直接在README.md中渲染
2. **Notion**: 复制Mermaid代码块
3. **VS Code**: 安装Mermaid插件预览
4. **在线编辑器**: https://mermaid.live

所有图表均基于真实代码路径绘制，准确反映了当前系统的执行流程。
