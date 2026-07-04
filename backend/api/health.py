from fastapi import APIRouter
from rag.retriever import get_health_report

router = APIRouter()


@router.get("/{project_id}")
def health_check(project_id: str):
    try:
        report = get_health_report(project_id)
        return report
    except Exception as e:
        return {"error": str(e)}