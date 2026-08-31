from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred.",
        headers: Optional[Dict[str, str]] = None,
        code: str = "INTERNAL_ERROR"
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code=code)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials", code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            code=code
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access forbidden for this tenant or role", code: str = "FORBIDDEN"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code=code)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Invalid request parameters", code: str = "BAD_REQUEST"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code=code)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource conflict or duplicate", code: str = "CONFLICT"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code=code)


class TenantMismatchException(ForbiddenException):
    def __init__(self, detail: str = "Cross-tenant access violation detected", code: str = "TENANT_MISMATCH"):
        super().__init__(detail=detail, code=code)
