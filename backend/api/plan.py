from fastapi import APIRouter
from pydantic import BaseModel
from agents.planner_agent import analyze_change

router = APIRouter()


class PlanRequest(BaseModel):
    project_id: str
    change_request: str


@router.post("/")
def plan(request: PlanRequest):
    return analyze_change(request.project_id, request.change_request)