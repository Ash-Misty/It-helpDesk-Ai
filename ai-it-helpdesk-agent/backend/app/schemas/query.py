from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's IT-related problem description",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "My laptop is connected to Wi-Fi but I cannot access the internet."
            }
        }


class QueryResponse(BaseModel):
    success: bool
    message: str
    user_query: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Your IT helpdesk request has been received.",
                "user_query": "My laptop is connected to Wi-Fi but I cannot access the internet.",
            }
        }


class HealthResponse(BaseModel):
    status: str
