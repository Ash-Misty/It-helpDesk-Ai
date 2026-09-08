from typing import List, Dict, Any
from app.schemas.query import QueryRequest


class QueryService:
    def __init__(self):
        self.conversations: List[Dict[str, Any]] = []
        self.next_id = 1

    def process_query(self, request: QueryRequest) -> Dict[str, Any]:
        user_message = request.message.strip()

        user_entry = {
            "id": self.next_id,
            "role": "user",
            "message": user_message,
        }
        self.conversations.append(user_entry)
        self.next_id += 1

        assistant_message = (
            "Your IT helpdesk request has been received. "
            "AI diagnosis will be added in the next module."
        )
        assistant_entry = {
            "id": self.next_id,
            "role": "assistant",
            "message": assistant_message,
        }
        self.conversations.append(assistant_entry)
        self.next_id += 1

        return {
            "success": True,
            "message": assistant_message,
            "user_query": user_message,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.conversations)


query_service = QueryService()
