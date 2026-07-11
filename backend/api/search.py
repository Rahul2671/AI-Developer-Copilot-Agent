from fastapi import APIRouter
from pydantic import BaseModel
from rag.retriever import search_codebase, get_indexed_files

router = APIRouter()


class SearchRequest(BaseModel):
    project_id: str
    query: str
    top_k: int = 10


@router.post("/")
def search(request: SearchRequest):
    results = search_codebase(request.project_id, request.query, request.top_k)
    return {"results": results}


@router.get("/files/{project_id}")
def files(project_id: str):
    return {"files": get_indexed_files(project_id)}