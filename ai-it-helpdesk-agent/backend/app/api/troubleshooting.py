from fastapi import APIRouter, HTTPException
from app.schemas.troubleshooting import (
    TroubleshootingStartRequest,
    TroubleshootingContinueRequest,
    TroubleshootingResponse,
)
from app.services.troubleshooting_service import troubleshooting_service

router = APIRouter()


@router.post("/troubleshooting/start", response_model=dict)
def start_troubleshooting(request: TroubleshootingStartRequest):
    try:
        result = troubleshooting_service.start(request.ticket_id)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during troubleshooting.",
        ) from exc


@router.post("/troubleshooting/continue", response_model=dict)
def continue_troubleshooting(request: TroubleshootingContinueRequest):
    try:
        result = troubleshooting_service.continue_troubleshooting(
            request.ticket_id, answer=request.answer
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during troubleshooting.",
        ) from exc
