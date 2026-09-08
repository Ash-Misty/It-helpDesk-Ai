from fastapi import APIRouter, HTTPException
from app.schemas.knowledge import KnowledgeSearchRequest
from app.knowledge.knowledge_base import knowledge_base

router = APIRouter()


@router.get("/knowledge", response_model=dict)
def list_knowledge():
    return {
        "success": True,
        "count": knowledge_base.count(),
        "documents": knowledge_base.list_all(),
    }


@router.get("/knowledge/{document_id}", response_model=dict)
def get_knowledge_document(document_id: str):
    doc = knowledge_base.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"success": True, "document": doc.model_dump()}


@router.post("/knowledge/search", response_model=dict)
def search_knowledge(request: KnowledgeSearchRequest):
    results = knowledge_base.search(
        query=request.query,
        category=request.category,
        limit=request.limit,
    )
    return {
        "success": True,
        "query": request.query,
        "count": len(results),
        "results": results,
    }
