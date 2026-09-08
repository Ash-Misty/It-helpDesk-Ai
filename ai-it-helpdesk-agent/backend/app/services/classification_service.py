from app.schemas.classification import ClassificationRequest
from app.classifier.classifier import issue_classifier


class ClassificationService:
    def classify(self, request: ClassificationRequest) -> dict:
        message = request.message.strip()
        if not message:
            raise ValueError("Message cannot be empty.")

        result = issue_classifier.classify(message)
        return result


classification_service = ClassificationService()
