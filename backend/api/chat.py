from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import chat_with_agent

router = APIRouter()


class ChatRequest(BaseModel):
    project_id: str
    question: str


@router.post("/")
def chat(request: ChatRequest):
    response = chat_with_agent(request.project_id, request.question)
    return response