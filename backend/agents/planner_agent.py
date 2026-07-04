import os
import json
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_relevant_context

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_change(project_id, change_request):
    try:
        contexts, sources = get_relevant_context(project_id, change_request)
    except ValueError as e:
        return {"error": str(e)}

    combined_context = "\n\n".join(contexts)
    unique_sources = list(set(sources))

    prompt = f"""You are a senior software architect analyzing the impact of a proposed code change, BEFORE any code is written.

Relevant existing code from the project:
{combined_context}

Existing files found relevant: {", ".join(unique_sources)}

Proposed change: "{change_request}"

Respond ONLY in valid JSON, with this exact structure, and nothing else (no markdown, no preamble):
{{
  "affected_files": ["list of file paths likely to be touched"],
  "new_files_needed": ["list of new files that would need to be created"],
  "required_changes": ["short bullet list of what needs to change"],
  "risk_level": "Low, Medium, or High",
  "complexity_score": "a number from 1 to 10",
  "possible_breaking_points": ["things that could break because of this change"],
  "summary": "one or two sentence plain-English summary of the plan"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content.strip()

        # Clean up in case model wraps in markdown code fences
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        plan = json.loads(raw_text)
        plan["sources_used"] = unique_sources
        return plan

    except json.JSONDecodeError:
        return {
            "error": "Could not parse structured plan",
            "raw_response": raw_text
        }
    except Exception as e:
        return {"error": str(e)}