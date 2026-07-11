import os
import json
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import search_codebase, get_project_files, get_indexed_files

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "Semantic search across the whole indexed repository. Use this to find where something is implemented.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language or keyword search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a specific file by its exact path, to see code that wasn't captured by search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Exact relative file path, e.g. backend/rag/loader.py"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List every file path in the indexed project -- useful to find the right file name before reading it.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def _execute_tool(project_id, name, arguments):
    if name == "search_codebase":
        try:
            results = search_codebase(project_id, arguments.get("query", ""), top_k=5)
        except ValueError as e:
            return json.dumps({"error": str(e)})
        return json.dumps(results)

    if name == "read_file":
        file_path = arguments.get("file_path", "")
        files_data = get_project_files(project_id)
        match = next((f for f in files_data if f["path"] == file_path), None)
        if not match:
            return json.dumps({"error": f"File '{file_path}' not found in project."})
        content = match["content"]
        if len(content) > 4000:
            content = content[:4000] + "\n... [truncated]"
        return json.dumps({"path": file_path, "content": content})

    if name == "list_files":
        try:
            files = get_indexed_files(project_id)
        except ValueError:
            files = []
        return json.dumps({"files": files})

    return json.dumps({"error": f"Unknown tool: {name}"})


def ask_with_tools(project_id, question, max_iterations=5):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a coding assistant with tools to search and read a specific "
                "codebase. Use search_codebase to find relevant code, and read_file when "
                "you need to see a file's full contents. Always cite file paths and line "
                "numbers when you reference code in your final answer."
            ),
        },
        {"role": "user", "content": question},
    ]

    tool_calls_made = []

    for _ in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=800,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            return {
                "answer": f"[LLM unavailable: {str(e)}]",
                "tool_calls": tool_calls_made,
            }

        message = response.choices[0].message

        if not message.tool_calls:
            return {
                "answer": message.content,
                "tool_calls": tool_calls_made,
            }

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ],
        })

        for tc in message.tool_calls:
            try:
                arguments = json.loads(tc.function.arguments)
            except Exception:
                arguments = {}

            result = _execute_tool(project_id, tc.function.name, arguments)
            tool_calls_made.append({"tool": tc.function.name, "arguments": arguments})

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return {
        "answer": "Reached maximum tool-call iterations without a final answer.",
        "tool_calls": tool_calls_made,
    }
