from fastapi import APIRouter
from services.project_store import get_project

router = APIRouter()


@router.get("/{project_id}")
def get_project_info(project_id: str):
    project = get_project(project_id)
    if not project:
        return {"error": "Project not found"}
    return project