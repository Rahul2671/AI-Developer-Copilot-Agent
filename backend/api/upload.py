from fastapi import APIRouter, UploadFile
import shutil, os, uuid
from rag.retriever import index_project

router = APIRouter()


@router.post("/")
async def upload_repo(file: UploadFile):
    project_id = str(uuid.uuid4())[:8]
    folder = f"data/projects/{project_id}"
    os.makedirs(folder, exist_ok=True)

    zip_path = f"{folder}/repo.zip"
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    num_chunks = index_project(project_id)

    return {
        "project_id": project_id,
        "status": "indexed",
        "chunks": num_chunks
    }