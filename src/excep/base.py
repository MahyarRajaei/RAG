# app/exceptions/base.py
class AppError(Exception):
    """Base class for all application-level errors."""

    code: str = "internal_error"
    status_code: int = 500

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.__doc__ or "An error occurred"
        super().__init__(self.message)
