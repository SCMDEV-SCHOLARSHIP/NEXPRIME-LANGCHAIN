from fastapi import status
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException


class ValueNotExistException(StarletteHTTPException):  # example
    def __init__(self, value: object, detail: str | None = None) -> None:
        self.value = value
        msg = (
            detail if detail != None else f"Input value {self.value} does not exist"
        )  # default message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
