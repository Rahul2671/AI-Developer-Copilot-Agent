from fastapi import APIRouter
from pydantic import BaseModel
from agents.explain_agent import explain_file

router = APIRouter()


class ExplainRequest(BaseModel):
    project_id: str
    file_path: str


@router.post("/")
def explain(request: ExplainRequest):
    result = explain_file(request.project_id, request.file_path)
    return result
