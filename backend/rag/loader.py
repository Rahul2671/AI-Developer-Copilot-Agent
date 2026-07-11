import os
import zipfile

def extract_repo(project_id, upload_path="data/projects"):
    zip_path = f"{upload_path}/{project_id}/repo.zip"
    extract_to = f"{upload_path}/{project_id}/extracted"
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    return extract_to


def read_code_files(folder_path):
    code_extensions = (
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".cpp", ".cc", ".c", ".h", ".hpp",
        ".cs", ".go", ".rs", ".php", ".rb", ".swift",
        ".kt", ".kts", ".m", ".mm", ".scala",
        ".sql", ".html", ".css", ".scss",
        ".json", ".xml", ".yaml", ".yml",
        ".sh", ".bat", ".ps1"
    )

    files_data = []

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [
            d for d in dirs
            if d not in (
                "node_modules",
                ".git",
                "__pycache__",
                "venv",
                ".venv",
                "dist",
                "build"
            )
        ]

        for file in files:
            if file.lower().endswith(code_extensions):
                full_path = os.path.join(root, file)
                # Store a clean relative path (e.g. "backend/auth.py") instead of
                # the full extracted-folder path -- makes citations/search results readable.
                relative_path = os.path.relpath(full_path, folder_path)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    files_data.append({
                        "path": relative_path,
                        "content": content
                    })

                except Exception:
                    continue

    return files_data

def list_files(project_id, upload_path="data/projects"):
    extracted_folder = f"{upload_path}/{project_id}/extracted"
    files_data = read_code_files(extracted_folder)
    return [f["path"] for f in files_data]