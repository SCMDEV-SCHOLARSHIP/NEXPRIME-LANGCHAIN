from fastapi import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.cores.exceptions.error_code import ErrorCode


class SDSHTTPException(StarletteHTTPException):
    def __init__(
        self,
        value: object,
        error_code: ErrorCode,
        status_code: int,
        detail: str | None = None,
    ) -> None:
        self.value = value
        self.error_code = error_code
        if detail == None:
            detail = f"{error_code.value[0]} : {error_code.value[1]} - {value}"

        super().__init__(status_code=status_code, detail=detail)


class InvalidRequestException(SDSHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        super().__init__(value, error_code, status.HTTP_400_BAD_REQUEST, detail)


class ForbiddenAccessException(SDSHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        super().__init__(value, error_code, status.HTTP_403_FORBIDDEN, detail)


class InternalServerException(SDSHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        super().__init__(
            value, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR, detail
        )


class ExternalServiceException(SDSHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        super().__init__(
            value, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR, detail
        )
