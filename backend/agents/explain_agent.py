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

    prompt = f"""You are a senior developer explaining a code file to a teammate who has never seen it.

File: {file_path}

Code (split into labeled sections with line numbers):
{combined_code}

Write your explanation using exactly these four headings:

1. Purpose - what this file is for, in 1-2 sentences
2. Important classes/functions - a short list, one line each
3. Execution flow - how the pieces in this file work together, step by step
4. Possible improvements - 2-3 concrete, specific suggestions

Keep it concise and organized under those headings."""

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