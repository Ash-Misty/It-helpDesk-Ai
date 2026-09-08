from fastapi import APIRouter, HTTPException
from app.schemas.classification import ClassificationRequest, ClassificationResponse
from app.services.classification_service import classification_service

router = APIRouter()


@router.post("/classify", response_model=ClassificationResponse)
def classify_issue(request: ClassificationRequest):
    try:
        result = classification_service.classify(request)
        return ClassificationResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while classifying the issue.",
        ) from exc
