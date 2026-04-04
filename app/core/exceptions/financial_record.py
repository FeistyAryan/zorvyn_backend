from app.core.exceptions.base import AppBaseException

class RecordNotFoundError(AppBaseException):
    """Thrown when a record doesn't exist or belongs to another user."""
    def __init__(self, message: str = "Financial record not found"):
        super().__init__(message=message, status_code=404)

class InvalidTransactionError(AppBaseException):
    """Thrown for business logic violations (e.g., negative amounts)."""
    def __init__(self, message: str = "Invalid transaction data provided"):
        super().__init__(message=message, status_code=400)