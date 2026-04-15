from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol

from vector_store import SearchResults, VectorStore


class Tool(ABC):
    """Abstract base class for all tools"""

    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass


class CourseSearchTool(Tool):
    """Tool for searching course content with semantic course name matching"""

    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search

    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Zhipu AI tool definition for this tool"""
        return {
            "type": "function",
            "function": {
                "name": "search_course_content",
                "description": "Search course materials with smart course name matching and lesson filtering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for in the course content",
                        },
                        "course_name": {
                            "type": "string",
                            "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')",
                        },
                        "lesson_number": {
                            "type": "integer",
                            "description": "Specific lesson number to search within (e.g. 1, 2, 3)",
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    def execute(
        self, query: str, course_name: Optional[str] = None, lesson_number: Optional[int] = None
    ) -> str:
        """
        Execute the search tool with given parameters.

        Args:
            query: What to search for
            course_name: Optional course filter
            lesson_number: Optional lesson filter

        Returns:
            Formatted search results or error message
        """

        # Use the vector store's unified search interface
        results = self.store.search(
            query=query, course_name=course_name, lesson_number=lesson_number
        )

        # Handle errors
        if results.error:
            return results.error

        # Handle empty results
        if results.is_empty():
            filter_info = ""
            if course_name:
                filter_info += f" in course '{course_name}'"
            if lesson_number:
                filter_info += f" in lesson {lesson_number}"
            return f"No relevant content found{filter_info}."

        # Format and return results
        return self._format_results(results)

    def _format_results(self, results: SearchResults) -> str:
        """Format search results with course and lesson context"""
        formatted = []
        sources = []  # Track sources for the UI

        for doc, meta in zip(results.documents, results.metadata):
            course_title = meta.get("course_title", "unknown")
            lesson_num = meta.get("lesson_number")

            # Retrieve course and lesson links
            course_link = self.store.get_course_link(course_title)
            lesson_link = None
            if lesson_num is not None:
                lesson_link = self.store.get_lesson_link(course_title, lesson_num)

            # Build context header
            header = f"[{course_title}"
            if lesson_num is not None:
                header += f" - Lesson {lesson_num}"
            header += "]"

            # Track source for the UI as structured object
            source = {
                "course_title": course_title,
                "lesson_number": lesson_num,
                "course_link": course_link,
                "lesson_link": lesson_link,
            }
            sources.append(source)

            formatted.append(f"{header}\n{doc}")

        # Store sources for retrieval
        self.last_sources = sources

        return "\n\n".join(formatted)


class CourseOutlineTool(Tool):
    """Tool for retrieving course outlines with lesson lists"""

    def __init__(self, vector_store: VectorStore):
        self.store = vector_store

    def get_tool_definition(self) -> Dict[str, Any]:
        """Return Zhipu AI tool definition for this tool"""
        return {
            "type": "function",
            "function": {
                "name": "get_course_outline",
                "description": "Get the complete outline of a course including all lessons",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_title": {
                            "type": "string",
                            "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')",
                        }
                    },
                    "required": ["course_title"],
                },
            },
        }

    def execute(self, course_title: str) -> str:
        """
        Execute the outline tool to get course structure.

        Args:
            course_title: Title of the course to get outline for

        Returns:
            Formatted course outline or error message
        """
        # Get course metadata with fuzzy matching
        course_meta = self.store.get_course_metadata(course_title)

        # Handle not found
        if not course_meta:
            return f"Course '{course_title}' not found."

        # Extract course information
        title = course_meta.get("title", "Unknown Course")
        course_link = course_meta.get("course_link")
        instructor = course_meta.get("instructor")
        lessons = course_meta.get("lessons", [])

        # Build formatted outline
        outline_parts = []

        # Course header
        outline_parts.append(f"**Course: {title}**")
        if course_link:
            outline_parts.append(f"Course Link: {course_link}")
        if instructor:
            outline_parts.append(f"Instructor: {instructor}")

        # Lessons list
        if lessons:
            outline_parts.append("\n**Lessons:**")
            for lesson in lessons:
                lesson_num = lesson.get("lesson_number")
                lesson_title = lesson.get("lesson_title")
                lesson_link = lesson.get("lesson_link")

                if lesson_num is not None and lesson_title:
                    if lesson_link:
                        outline_parts.append(
                            f"- Lesson {lesson_num}: {lesson_title} ({lesson_link})"
                        )
                    else:
                        outline_parts.append(f"- Lesson {lesson_num}: {lesson_title}")
        else:
            outline_parts.append("\nNo lessons available for this course.")

        return "\n".join(outline_parts)


class ToolManager:
    """Manages available tools for the AI"""

    def __init__(self):
        self.tools = {}
        self.accumulated_sources = []  # Track accumulated sources from sequential tool calls

    def register_tool(self, tool: Tool):
        """Register any tool that implements the Tool interface"""
        tool_def = tool.get_tool_definition()
        # Handle Zhipu AI format with nested function
        if "function" in tool_def:
            tool_name = tool_def["function"].get("name")
        else:
            tool_name = tool_def.get("name")
        if not tool_name:
            raise ValueError("Tool must have a 'name' in its definition")
        self.tools[tool_name] = tool

    def get_tool_definitions(self) -> list:
        """Get all tool definitions for Anthropic tool calling"""
        return [tool.get_tool_definition() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"

        return self.tools[tool_name].execute(**kwargs)

    def get_last_sources(self) -> list:
        """Get accumulated sources from all tool executions"""
        return self.accumulated_sources

    def reset_sources(self):
        """Reset all accumulated and last sources"""
        self.accumulated_sources = []
        for tool in self.tools.values():
            if hasattr(tool, "last_sources"):
                tool.last_sources = []

    def accumulate_sources(self):
        """Move last_sources to accumulated_sources"""
        for tool in self.tools.values():
            if hasattr(tool, "last_sources") and tool.last_sources:
                # Avoid duplicates
                for source in tool.last_sources:
                    if source not in self.accumulated_sources:
                        self.accumulated_sources.append(source)
