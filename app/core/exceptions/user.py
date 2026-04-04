from app.core.exceptions.base import AppBaseException

class UserAlreadyExistsError(AppBaseException):
    """Thrown during signup if email is taken."""
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message=message, status_code=400)

class UserNotFoundError(AppBaseException):
    """Thrown when looking for a non-existent user."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message=message, status_code=404)