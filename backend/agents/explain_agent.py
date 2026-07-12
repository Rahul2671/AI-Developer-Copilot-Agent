import os
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_file_chunks

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def explain_file(project_id, file_path):
    try:
        chunks = get_file_chunks(project_id, file_path)
    except ValueError as e:
        return {"file": file_path, "explanation": str(e)}

    if not chunks:
        return {
            "file": file_path,
            "explanation": (
                "This file wasn't found in the indexed project. "
                "Use the exact path returned by the file list or search endpoint."
            ),
        }

    labeled_blocks = []
    for chunk in chunks:
        label = f"Lines {chunk['start_line']}-{chunk['end_line']}"
        if chunk.get("symbol"):
            label += f" - {chunk['kind']} {chunk['symbol']}"
        labeled_blocks.append(f"### {label}\n{chunk['text']}")
    combined_code = "\n\n".join(labeled_blocks)

    prompt = f"""
You are an expert Software Engineer performing a code walkthrough for another developer.

The following file comes from an existing software project.

File:
{file_path}

Retrieved code:
{combined_code}

Your task is to explain ONLY what exists in this file.
Do NOT invent behaviour that is not present in the code.
If something cannot be determined from this file alone, explicitly say so.

Produce the explanation using the following sections.

# Overview
Explain the overall purpose of this file in 2-3 sentences.

# File Type
Identify what kind of file this is, for example:
- React Component
- Express Route
- FastAPI Router
- Controller
- Service
- Utility
- Database Model
- Middleware
- Configuration
- API Client
- Other

Explain why.

# Main Responsibilities
List the major responsibilities handled by this file.

# Important Functions / Classes
For every important function or class:
- Name
- Purpose
- Inputs
- Outputs
- Important logic

# Execution Flow
Explain how execution typically flows through this file from start to finish.

# Dependencies
Mention important imports and explain why they are used.

# Interactions
Explain how this file communicates with other parts of the application whenever it is evident from the code.

# Possible Improvements
Suggest only improvements that are directly relevant to the existing implementation.
Avoid generic suggestions.

Keep the explanation concise, technical, and easy for another developer to understand.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.choices[0].message.content
    except Exception:
        explanation = f"[LLM unavailable — showing raw file chunks]\n\n{combined_code[:1200]}"

    return {
        "file": file_path,
        "explanation": explanation,
        "chunk_count": len(chunks),
    }