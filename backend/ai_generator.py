from typing import Dict, List, Optional, Tuple

import zhipuai


class AIGenerator:
    """Handles interactions with Zhipu AI API for generating responses"""

    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """You are a course assistant with access to course materials through search tools.

**CRITICAL: Tool Usage Requirement**
- You MUST use the appropriate tool for course-related questions
- Do NOT answer from your training data - always search first

**Sequential Tool Calling:**
- You can call up to 2 tools consecutively to answer complex questions
- Use sequential calls when:
  * First tool provides information needed for a second tool
  * User asks about multiple topics that require different tools
  * First search returns insufficient or incomplete results
- Examples of sequential calling:
  * "What courses cover RAG and what are their outlines?"
    → First call: search_course_content(query="RAG")
    → Second call: get_course_outline for found courses
  * "Tell me about MCP and show me the course structure"
    → First call: search_course_content(query="MCP")
    → Second call: get_course_outline(course_title="Introduction to MCP")

**Tool Selection:**

1. **search_course_content** - Use for questions about course content:
   - Technical concepts, explanations, definitions
   - "What is RAG?", "How does Chroma work?", "Explain MCP"
   - Specific topics within course materials
   - Parameters: query (required), course_name (optional), lesson_number (optional)

2. **get_course_outline** - Use for questions about course structure:
   - "Show me the outline", "What lessons are in this course?"
   - "Course structure", "Course overview", "List of lessons"
   - Returns: course title, course link, instructor, and complete lesson list with lesson numbers and titles
   - Parameters: course_title (required)

**Questions that DON'T require tools:**
- Greetings, "how do you work", system questions
- General conversation not related to course content

**Tool Calling Protocol:**
1. Analyze the user's question to determine which tool(s) are needed
2. For single-tool questions: make one appropriate tool call
3. For multi-tool questions:
   - Make the first tool call with relevant parameters
   - Use results to inform the second tool call
   - Maximum 2 consecutive tool calls allowed
4. After receiving tool results, formulate your answer based ONLY on those results
5. If no results found, state this clearly
6. Always use tool results - never fabricate information

**Response Format:**
- Direct, concise answers
- Based on tool results only
- Educational and clear
- No meta-commentary about the tool process
"""

    def __init__(self, api_key: str, model: str):
        self.client = zhipuai.ZhipuAI(api_key=api_key)
        self.model = model

    def generate_response(
        self,
        query: str,
        conversation_history: Optional[str] = None,
        tools: Optional[List] = None,
        tool_manager=None,
        max_rounds: int = 2,
    ) -> str:
        """
        Generate AI response with optional tool usage and conversation context.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            max_rounds: Maximum number of tool calling rounds (default: 2)

        Returns:
            Generated response as string
        """

        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        # Prepare messages
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ]

        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 800,
        }

        # Add tools if available
        if tools:
            api_params["tools"] = tools

        # Get response from Zhipu AI
        response = self.client.chat.completions.create(**api_params)

        # Handle tool execution if needed
        if response.choices[0].message.tool_calls and tool_manager:
            return self._handle_tool_execution(response, messages, tool_manager, max_rounds)

        # Return direct response
        return response.choices[0].message.content

    def _handle_tool_execution(
        self, initial_response, messages: List[Dict], tool_manager, max_rounds: int = 2
    ) -> str:
        """
        Handle sequential tool execution with up to 2 rounds.

        Args:
            initial_response: The response containing tool use requests
            messages: Existing message history
            tool_manager: Manager to execute tools
            max_rounds: Maximum number of tool calling rounds (default: 2)

        Returns:
            Final response text after tool execution
        """
        current_messages = messages.copy()
        current_response = initial_response
        current_round = 0
        tools = tool_manager.get_tool_definitions()

        # 循环处理最多max_rounds轮工具调用
        while current_round < max_rounds:
            # 终止条件1: AI不想要使用工具
            if not current_response.choices[0].message.tool_calls:
                break

            # 执行当前轮的工具
            try:
                assistant_message, tool_results = self._execute_tools_round(
                    current_response, tool_manager
                )

                # 更新消息历史
                current_messages.append(assistant_message)
                current_messages.extend(tool_results)

                # 累积源
                tool_manager.accumulate_sources()

                # 终止条件2: 工具执行失败
                if self._has_execution_errors(tool_results):
                    break

            except Exception as e:
                # 处理工具执行异常
                print(f"Tool execution error: {e}")
                break

            # 准备下一轮API调用
            current_round += 1
            if current_round >= max_rounds:
                break

            # 进行下一轮API调用（保持工具可用）
            current_response = self._make_api_call(current_messages, tools=tools)

        # 最终API调用（不包含工具）
        final_response = self._make_api_call(current_messages, tools=None)
        return final_response.choices[0].message.content

    def _execute_tools_round(self, response, tool_manager) -> Tuple[Dict, List[Dict]]:
        """
        Execute all tool calls in a single round.

        Args:
            response: API response containing tool calls
            tool_manager: Manager to execute tools

        Returns:
            Tuple of (assistant_message, tool_results_messages)
        """
        # Build assistant message with tool_calls
        assistant_message = {
            "role": "assistant",
            "content": response.choices[0].message.content or "",
            "tool_calls": [],
        }

        tool_results = []

        for tool_call in response.choices[0].message.tool_calls:
            # Parse arguments
            import json

            try:
                arguments = json.loads(tool_call.function.arguments)
            except:
                arguments = {}

            # Execute tool
            tool_result = tool_manager.execute_tool(tool_call.function.name, **arguments)

            # Build tool_call entry
            assistant_message["tool_calls"].append(
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            )

            # Build tool result message
            tool_results.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result}
            )

        return assistant_message, tool_results

    def _make_api_call(self, messages: List[Dict], tools: Optional[List] = None) -> Dict:
        """
        Make API call with optional tools parameter.

        Args:
            messages: Complete message history
            tools: Tool definitions (include for intermediate rounds, exclude for final)

        Returns:
            API response object
        """
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 800,
        }

        if tools:
            api_params["tools"] = tools

        return self.client.chat.completions.create(**api_params)

    def _has_execution_errors(self, tool_results: List[Dict]) -> bool:
        """
        Check if any tool executions failed.

        Args:
            tool_results: List of tool result messages

        Returns:
            True if any tool execution contained errors
        """
        for result in tool_results:
            content = result.get("content", "")
            # Check for common error indicators
            error_indicators = ["error", "failed", "not found", "exception"]
            if any(indicator in content.lower() for indicator in error_indicators):
                return True
        return False
