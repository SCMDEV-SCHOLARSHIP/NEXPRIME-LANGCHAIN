from collections.abc import Callable, Coroutine
from typing import Any
from fastapi import Request, Response

from .exceptions import (
    ValueNotExistException,
    InvalidRequestException,
    HTTPException,
    StarletteHTTPException,
)
from app.cores.exceptions import handlers


EXC_HDLRs: dict[
    int | type[Exception], Callable[[Request, Exception], Coroutine[Any, Any, Response]]
] = {
    ValueNotExistException: handlers.value_not_exist_handler,
    InvalidRequestException: handlers.bad_request_handler,
    404: handlers.not_found_error,
}