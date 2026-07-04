import os
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_relevant_context

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_codebase(project_id, question):
    try:
        contexts, sources = get_relevant_context(project_id, question)
    except ValueError as e:
        return {"answer": str(e), "sources": []}

    if not contexts:
        return {"answer": "No relevant code found for this question.", "sources": []}

    combined_context = "\n\n".join(contexts)

    prompt = f"""You are a helpful AI assistant that answers questions about a codebase.

Relevant code from the project:
{combined_context}

Question: {question}

Answer clearly and concisely, referencing the code above."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"[LLM unavailable — showing raw retrieved code]\n\n{combined_context[:800]}"

    return {
        "answer": answer,
        "sources": sources
    }