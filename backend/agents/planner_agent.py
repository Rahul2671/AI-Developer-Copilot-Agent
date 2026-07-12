import os
import json
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_relevant_context

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_change(project_id, change_request):
    try: 
        chunks = get_relevant_context(project_id, change_request)
    except ValueError as e:
        return {"error": str(e)}
    
    if not chunks:
        return {
            "summary": "No relevant code was found for this request.",
            "affected_files": [],
            "new_files_needed": [],
            "required_changes": [],
            "risk_level": "Unknown",
            "complexity_score": 0,
            "possible_breaking_points": [],
            "sources_used": []
        }

    combined_context = "\n\n".join(chunk["text"] for chunk in chunks)
    unique_sources = sorted(set(chunk["source"] for chunk in chunks))

    prompt = f"""
You are an expert Software Architect and Senior Tech Lead.

Your job is to analyze a proposed feature or code change BEFORE implementation.

Only use information found in the retrieved repository context.

Do NOT invent files, APIs, classes or architecture that do not exist.

If the retrieved context is insufficient, explicitly mention that in the summary instead of guessing.

Repository Context:
{combined_context}

Relevant Existing Files:
{", ".join(unique_sources)}

Requested Change:
{change_request}

Think about:

- Which existing files must change
- Which new files are required
- Database changes (if applicable)
- API endpoint changes
- UI changes
- Authentication/authorization impact
- Dependencies that may be affected
- Possible breaking changes
- Performance implications
- Security considerations
- Testing requirements
- Estimated implementation complexity

Return ONLY valid JSON.

{{
  "summary": "High level explanation",

  "affected_files": [
    {{
      "file": "path",
      "reason": "why this file changes"
    }}
  ],

  "new_files_needed": [
    {{
      "file": "path",
      "purpose": "why this file is needed"
    }}
  ],

  "required_changes": [
    "step 1",
    "step 2",
    "step 3"
  ],

  "api_changes": [
    "new endpoints",
    "modified endpoints"
  ],

  "database_changes": [
    "collections/tables affected"
  ],

  "security_considerations": [
    "authentication",
    "authorization",
    "validation"
  ],

  "performance_considerations": [
    "possible bottlenecks"
  ],

  "testing_required": [
    "unit tests",
    "integration tests",
    "UI tests"
  ],

  "possible_breaking_points": [
    "list"
  ],

  "risk_level": "Low | Medium | High",

  "complexity_score": 1,

  "estimated_effort": "Small | Medium | Large",

  "implementation_order": [
    "step 1",
    "step 2",
    "step 3"
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[
                {
                    "role":"system",
                    "content":(
                        "You are an expert software architect. "
                        "Return only valid JSON. "
                        "Never invent project files or APIs. "
                        "Use only the supplied repository context."
                    )
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ]
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