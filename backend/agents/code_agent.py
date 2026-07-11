import os
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_relevant_context

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _format_citation(chunk):
    location = f"{chunk['source']} (Lines {chunk['start_line']}-{chunk['end_line']})"
    if chunk.get("symbol"):
        location += f" - {chunk['kind']} {chunk['symbol']}"
    return location


def _dedupe_sources(chunks):
    seen = set()
    sources = []
    for chunk in chunks:
        key = (chunk["source"], chunk["start_line"], chunk["end_line"])
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "file": chunk["source"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "symbol": chunk.get("symbol"),
            "kind": chunk.get("kind"),
        })
    return sources


def ask_codebase(project_id, question):
    try:
        chunks = get_relevant_context(project_id, question)
    except ValueError as e:
        return {"answer": str(e), "sources": []}

    if not chunks:
        return {"answer": "No relevant code found for this question.", "sources": []}

    labeled_blocks = []
    for chunk in chunks:
        label = _format_citation(chunk)
        labeled_blocks.append(f"### {label}\n{chunk['text']}")
    combined_context = "\n\n".join(labeled_blocks)

    prompt = f"""You are a helpful AI assistant that answers questions about a codebase.

Each snippet below is labeled with its file name, line numbers, and function/class name.

{combined_context}

Question: {question}

Answer clearly and concisely, referencing the code above. When you refer to a
specific piece of code, mention which file and function it came from."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
    except Exception:
        answer = f"[LLM unavailable — showing raw retrieved code]\n\n{combined_context[:800]}"

    sources = _dedupe_sources(chunks)

    if sources:
        lines = []
        for s in sources:
            line = f"{s['file']} (Lines {s['start_line']}-{s['end_line']})"
            if s.get("symbol"):
                line += f" - {s['kind']} {s['symbol']}"
            lines.append(f"- {line}")
        answer = f"{answer}\n\nSources:\n" + "\n".join(lines)

    return {
        "answer": answer,
        "sources": sources
    }