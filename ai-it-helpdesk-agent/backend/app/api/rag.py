from fastapi import APIRouter, HTTPException
from app.schemas.knowledge import KnowledgeSearchRequest
from app.rag.pipeline import rag_pipeline

router = APIRouter()


@router.post("/rag/search", response_model=dict)
def search_rag(request: KnowledgeSearchRequest):
    result = rag_pipeline.search(
        query=request.query,
        top_k=request.limit,
        category=request.category,
    )
    return result
