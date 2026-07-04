from fastapi import APIRouter
from pydantic import BaseModel
from rag.loader import list_files
from agents.review_agent import review_file

router = APIRouter()


@router.get("/files/{project_id}")
def get_files(project_id: str):
    try:
        files = list_files(project_id)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}


class ReviewRequest(BaseModel):
    project_id: str
    file_path: str


@router.post("/")
def review(request: ReviewRequest):
    return review_file(request.project_id, request.file_path)