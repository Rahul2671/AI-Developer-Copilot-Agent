import os
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_relevant_context
from rag.memory import get_history, append_turn

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


def _format_history(history):
    if not history:
        return ""
    lines = []
    for turn in history[-10:]:
        role = "You" if turn["role"] == "assistant" else "Developer"
        lines.append(f"{role}: {turn['content']}")
    return "\n".join(lines)


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
    if not combined_context.strip():
        return {
            "answer": (
                "I couldn't find enough relevant code to answer this question.\n\n"
                "Try:\n"
                "- using more specific function or file names\n"
                "- asking about a particular feature\n"
                "- making sure the repository was indexed successfully"
            ),
            "sources": []
        }

    history = get_history(project_id)
    history_text = _format_history(history)
    history_section = f"\nPrevious conversation about this project:\n{history_text}\n" if history_text else ""

    prompt = f"""
You are an expert AI Software Engineer and Software Architect.

You are answering questions about an existing software project.

{history_section}

Relevant repository context:

{combined_context}

User Question:
{question}

Instructions:

- Answer ONLY using the provided repository context and previous conversation.
- Never invent files, functions, APIs, classes or behaviour that are not present in the retrieved code.
- If the available context is insufficient, clearly explain what information is missing instead of guessing.
- Speak confidently when the retrieved code clearly answers the question.
- Avoid phrases like "Based on the provided snippets..." unless information is genuinely incomplete.
- If multiple files are involved, explain how they work together.
- When appropriate, explain:
  • Overall purpose
  • Execution flow
  • Important functions/classes
  • Interactions between components
  • Edge cases
  • Design decisions

Formatting:

## Overview
Give a short explanation.

## Details
Explain the implementation clearly.

## Key Components
• Component — purpose
• Component — purpose

## Sources
Mention the relevant files naturally in your explanation.

Keep the response concise but complete.

Prioritize practical explanations over theoretical ones.

If explaining a feature, describe:
- what it does
- how it works
- which files participate
- important execution flow
- important design choices
- possible limitations if visible

Never fabricate implementation details.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software architect and staff-level software engineer."
                        "You answer questions ONLY using the retrieved repository context."
                        "Never invent files, functions, APIs, variables or behaviour."
                        "If the repository context is insufficient, explicitly say what information is missing instead of guessing."
                        "Always produce technically accurate, structured, concise explanations."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        answer = response.choices[0].message.content
    except Exception:
        answer = (
            "The AI model is currently unavailable.\n\n"
            "Relevant code was successfully retrieved from the repository.\n"
            "Review the snippet below while the AI service is unavailable:\n\n"
            f"{combined_context[:1200]}"
        )

    append_turn(project_id, question, answer)

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
