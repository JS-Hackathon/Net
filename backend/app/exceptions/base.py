class AppException(Exception):
    """Base exception for all system business exceptions."""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")

class ForbiddenError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")

class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: list = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")
        self.details = details or []
