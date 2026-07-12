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
            "description": "Search the indexed repository for functions, classes, APIs, variables, routes, database models, UI components, configuration files, or implementation details relevant to the user's question.",
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
            "description": "Read the complete source code of a specific file after locating it via search or when the exact file path is already known.",
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
            "description": "Return all indexed file paths. Use this only when the correct filename or location is unknown.",
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
        if len(content) > 8000:
            content = content[:8000] + "\n... [truncated]"
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
                "You are an expert AI Software Engineer with access to tools for exploring a software repository.\n\n"

                "# General Rules\n"
                "- Always answer using information from the repository.\n"
                "- Never invent files, functions, APIs, classes, or behavior.\n"
                "- If the available context is insufficient, say so instead of guessing.\n"
                "- Use repository evidence before relying on general programming knowledge.\n\n"

                "# Tool Usage\n"
                "- Use search_codebase first to locate relevant code.\n"
                "- Use read_file only after search results or when an exact file path is provided.\n"
                "- Use list_files if you cannot determine the correct file name.\n"
                "- Minimize unnecessary tool calls.\n"
                "- Never output function calls, XML tags, or JSON representing tool calls in your response.\n"
                "- Invoke tools only through the provided tool interface.\n\n"

                "# Answer Quality\n"
                "- Explain your reasoning clearly and logically.\n"
                "- Describe how different components work together.\n"
                "- Mention important functions, classes, APIs, or modules involved.\n"
                "- Highlight design decisions, dependencies, and possible edge cases when relevant.\n"
                "- Keep explanations concise but technically complete.\n"
                "- If multiple files contribute to the feature, explain their relationship.\n\n"

                "# Evidence\n"
                "- Cite file paths and line numbers whenever repository evidence is available.\n"
                "- Do not cite files that were not retrieved.\n\n"

                "# Restrictions\n"
                "- Never hallucinate missing code.\n"
                "- Never fabricate implementation details.\n"
                "- If the repository does not contain the requested information, clearly state that instead of guessing."
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
