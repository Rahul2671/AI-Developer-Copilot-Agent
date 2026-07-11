import os
from dotenv import load_dotenv
from groq import Groq
from rag.retriever import get_project_files
from rag.architecture import build_tech_stack, build_folder_summary, detect_entry_points

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_architecture_summary(project_id):
    files_data = get_project_files(project_id)
    if not files_data:
        return {"summary": "No files found for this project. Make sure it was uploaded first."}

    tech_stack = build_tech_stack(files_data)
    folder_summary = build_folder_summary(files_data)
    entry_points = detect_entry_points(files_data)

    folder_lines = "\n".join(
        f"- {f['folder']}/ ({f['file_count']} files): {', '.join(f['files'][:8])}"
        for f in folder_summary
    )
    stack_lines = "\n".join(
        f"{category}: {', '.join(names)}" for category, names in tech_stack.items()
    )

    prompt = f"""You are a senior software architect. Based on this project's folder structure and tech stack, write a concise architecture summary.

Tech stack detected:
{stack_lines}

Entry point files:
{', '.join(entry_points) if entry_points else 'None detected'}

Folder structure:
{folder_lines}

Write:
1. A short paragraph (3-5 sentences) describing the overall architecture and how the pieces likely fit together.
2. A simple text-based layered diagram (using arrows like "->") showing the flow, e.g. Frontend -> API -> Services -> Database.

Keep it concise and accurate to what's actually shown above -- do not invent components that aren't evidenced by the folder structure or tech stack."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content
    except Exception:
        summary = f"[LLM unavailable — showing raw structure]\n\nTech stack:\n{stack_lines}\n\nFolders:\n{folder_lines}"

    return {
        "summary": summary,
        "tech_stack": tech_stack,
        "folder_summary": folder_summary,
        "entry_points": entry_points,
    }


def explain_folder(project_id, folder_path):
    files_data = get_project_files(project_id)
    normalized = folder_path.rstrip("/")
    matches = [f for f in files_data if os.path.dirname(f["path"]) == normalized]

    if not matches:
        return {
            "folder": folder_path,
            "explanation": "No files found in this folder. Check the exact folder path from the folder list.",
        }

    previews = []
    for f in matches:
        preview_lines = f["content"].splitlines()[:40]
        preview = "\n".join(preview_lines)
        previews.append(f"### {f['path']}\n{preview}")
    combined = "\n\n".join(previews)

    prompt = f"""You are a senior developer explaining a folder to a teammate.

Folder: {folder_path}
Files in this folder (each shown with a preview of its first lines):

{combined}

For each file, write ONE short line describing its purpose. Then write a 2-3 sentence summary of what this folder as a whole is responsible for."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.choices[0].message.content
    except Exception:
        explanation = f"[LLM unavailable — showing raw folder contents]\n\n{combined[:1200]}"

    return {
        "folder": folder_path,
        "explanation": explanation,
        "file_count": len(matches),
    }
