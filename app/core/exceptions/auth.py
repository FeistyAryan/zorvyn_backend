from app.core.exceptions.base import AppBaseException

class AuthenticationError(AppBaseException):
    """Thrown when login or token verification fails."""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message, 
            status_code=401, 
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenError(AppBaseException):
    """Thrown when user lacks permission (e.g., Viewer trying to Delete)."""
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message=message, status_code=403)

class UserAlreadyExistsError(AppBaseException):
    """Thrown when a user with the same email already exists."""
    def __init__(self, message: str = "User with this email already exists."):
        super().__init__(message=message, status_code=400)