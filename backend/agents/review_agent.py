import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def review_file(project_id, file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(
            "data",
            "projects",
            project_id,
            "extracted",
            file_path
        )
    if not os.path.exists(file_path):
        return {
            "error": f"File not found: {file_path}"
        }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except FileNotFoundError:
        return {"error": "File not found"}

    prompt = f"""
You are an experienced Staff Software Engineer performing a professional code review.

Review ONLY the code below.

File:
{file_path}

Source Code:
{content}

Instructions:

- Identify only real issues supported by the code.
- Do NOT invent problems.
- Ignore formatting/style unless it affects maintainability.
- Focus on:
  • Bugs
  • Security vulnerabilities
  • Performance issues
  • Error handling
  • Code smells
  • Maintainability
  • Scalability
  • Best practices

For every issue provide:

Severity: High / Medium / Low

Location:
(function name, class name or approximate line)

Problem:
(what is wrong)

Why it matters:
(short explanation)

Recommended fix:
(concrete improvement)

Code example (only if useful):
(short snippet)

If the code is already good, explicitly say

"No significant issues found."

Finally provide:

## Overall Code Quality
Rate the file out of 10.

## Priority Fixes
List the three most important improvements developers should implement first.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        review = response.choices[0].message.content
    except Exception as e:
        review = (
            "The AI reviewer is currently unavailable.\n\n"
            "The file was successfully loaded, but the review model could not generate an analysis.\n\n"
            f"Reason: {str(e)}"
        )

    return {"file": file_path, "review": review}