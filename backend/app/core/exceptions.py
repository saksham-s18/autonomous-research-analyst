class AppException(Exception):
    """Base exception for expected application errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code

        super().__init__(message)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        code: str = "RESOURCE_NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=404,
        )