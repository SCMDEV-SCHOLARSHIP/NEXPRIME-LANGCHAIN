from fastapi import status
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.cores.exceptions.error_code import ErrorCode


class ValueNotExistException(StarletteHTTPException):  # example
    def __init__(self, value: object, detail: ErrorCode | None = None) -> None:
        self.value = value
        if detail == None:
            detail = ErrorCode(
                code="KMG_ERR_R_001", message=f"Input value {self.value} does not exist"
            )

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidRequestException(StarletteHTTPException):
    def __init__(self, value: object, detail: ErrorCode | None = None) -> None:
        self.value = value
        if detail == None:
            detail = ErrorCode(
                code="KMG_ERR_R_002", message=f"{self.value} : Bad Request"
            )

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
