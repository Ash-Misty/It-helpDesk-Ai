from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse, HealthResponse
from app.services.query_service import query_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy")


@router.post("/queries", response_model=QueryResponse)
def create_query(request: QueryRequest):
    try:
        result = query_service.process_query(request)
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request.",
        ) from exc
