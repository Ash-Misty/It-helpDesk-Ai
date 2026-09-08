from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's IT-related problem description to classify",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "My laptop is connected to Wi-Fi but I cannot access the internet."
            }
        }


class ClassificationResponse(BaseModel):
    success: bool
    category: str
    subcategory: str
    priority: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "category": "Network",
                "subcategory": "Internet Connectivity",
                "priority": "Medium",
                "confidence": 0.92,
                "reason": "The query indicates an internet connectivity problem.",
            }
        }
