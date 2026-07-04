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
    code_extensions = (".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp")
    files_data = []

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__", "venv")]
        for file in files:
            if file.endswith(code_extensions):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    files_data.append({"path": full_path, "content": content})
                except Exception:
                    continue

    return files_data