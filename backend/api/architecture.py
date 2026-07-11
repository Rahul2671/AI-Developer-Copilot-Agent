from fastapi import APIRouter
from pydantic import BaseModel
from agents.architecture_agent import generate_architecture_summary, explain_folder
from rag.retriever import get_project_files
from rag.architecture import build_folder_summary

router = APIRouter()


class FolderExplainRequest(BaseModel):
    project_id: str
    folder_path: str


@router.get("/summary/{project_id}")
def summary(project_id: str):
    return generate_architecture_summary(project_id)


@router.post("/folder")
def folder(request: FolderExplainRequest):
    return explain_folder(request.project_id, request.folder_path)


@router.get("/folders/{project_id}")
def list_folders(project_id: str):
    """List every folder available for the 'explain folder' picker."""
    files_data = get_project_files(project_id)
    folder_summary = build_folder_summary(files_data)
    return {"folders": [f["folder"] for f in folder_summary]}
