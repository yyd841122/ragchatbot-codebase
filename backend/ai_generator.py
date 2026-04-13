import zhipuai
from typing import List, Optional, Dict

class AIGenerator:
    """Handles interactions with Zhipu AI API for generating responses"""

    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""

    def __init__(self, api_key: str, model: str):
        self.client = zhipuai.ZhipuAI(api_key=api_key)
        self.model = model

    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools

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
        messages = [{"role": "system", "content": system_content},
                   {"role": "user", "content": query}]

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
            api_params["tool_choice"] = {"type": "auto", "function": {"name": tools[0]["function"]["name"]}}

        # Get response from Zhipu AI
        response = self.client.chat.completions.create(**api_params)

        # Handle tool execution if needed
        if response.choices[0].message.tool_calls and tool_manager:
            return self._handle_tool_execution(response, messages, tool_manager)

        # Return direct response
        return response.choices[0].message.content

    def _handle_tool_execution(self, initial_response, messages: List[Dict], tool_manager):
        """
        Handle execution of tool calls and get follow-up response.

        Args:
            initial_response: The response containing tool use requests
            messages: Existing message history
            tool_manager: Manager to execute tools

        Returns:
            Final response text after tool execution
        """

        # Add AI's tool use response
        assistant_message = {
            "role": "assistant",
            "content": initial_response.choices[0].message.content or "",
            "tool_calls": []
        }

        # Execute all tool calls and collect results
        tool_results = []
        for tool_call in initial_response.choices[0].message.tool_calls:
            # Execute the tool
            tool_result = tool_manager.execute_tool(
                tool_call.function.name,
                **eval(tool_call.function.arguments)
            )

            # Add to assistant message
            assistant_message["tool_calls"].append({
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })

            # Add tool result message
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # Build messages for final call
        final_messages = messages.copy()
        final_messages.append(assistant_message)
        final_messages.extend(tool_results)

        # Prepare final API call without tools
        final_params = {
            "model": self.model,
            "messages": final_messages,
            "temperature": 0,
            "max_tokens": 800,
        }

        # Get final response
        final_response = self.client.chat.completions.create(**final_params)
        return final_response.choices[0].message.content
