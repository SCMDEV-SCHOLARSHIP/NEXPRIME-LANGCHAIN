from fastapi import status
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.cores.exceptions.error_code import ErrorCode


class InvalidRequestException(StarletteHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        self.value = value
        self.error_code = error_code
        if detail == None:
            detail = f"{ErrorCode.BAD_REQUEST.value[0]} : {ErrorCode.BAD_REQUEST.value[1]} - {value}"

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ExternalServiceException(StarletteHTTPException):
    def __init__(
        self, value: object, error_code: ErrorCode, detail: str | None = None
    ) -> None:
        self.value = value
        self.error_code = error_code
        if detail == None:
            detail = f"{ErrorCode.EXTERNAL_SERVICE_ERROR.value[0]} : {ErrorCode.EXTERNAL_SERVICE_ERROR.value[1]} - {value}"

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
