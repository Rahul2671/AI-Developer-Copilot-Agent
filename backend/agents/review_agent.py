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
    try:
        print(file_path)
        print(os.path.exists(file_path))
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except FileNotFoundError:
        return {"error": "File not found"}

    prompt = f"""You are a senior code reviewer. Review the following code for bugs, security issues, and bad practices.

File: {file_path}

Code:
{content}

Return your review as a numbered list. For each issue include:
- Severity (High/Medium/Low)
- Location (function or line, if identifiable)
- Issue description
- Suggested fix

If no issues are found, say "No issues found."
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        review = response.choices[0].message.content
    except Exception as e:
        review = f"Review unavailable: {str(e)}"

    return {"file": file_path, "review": review}
