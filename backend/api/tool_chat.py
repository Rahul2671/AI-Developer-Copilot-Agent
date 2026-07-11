from fastapi import APIRouter
from pydantic import BaseModel
from agents.tool_agent import ask_with_tools

router = APIRouter()


class ToolChatRequest(BaseModel):
    project_id: str
    question: str


@router.post("/")
def tool_chat(request: ToolChatRequest):
    return ask_with_tools(request.project_id, request.question)
