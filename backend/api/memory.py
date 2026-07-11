from fastapi import APIRouter
from rag.memory import get_history, clear_history

router = APIRouter()


@router.get("/{project_id}")
def history(project_id: str):
    return {"history": get_history(project_id)}


@router.delete("/{project_id}")
def clear(project_id: str):
    clear_history(project_id)
    return {"status": "cleared"}
