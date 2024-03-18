from collections.abc import Callable, Coroutine
from typing import Any
from fastapi import Request, Response

from .exceptions import (
    InvalidRequestException,
    ExternalServiceException,
    HTTPException,
    StarletteHTTPException,
)
from app.cores.exceptions import handlers


EXC_HDLRs: dict[
    int | type[Exception], Callable[[Request, Exception], Coroutine[Any, Any, Response]]
] = {
    InvalidRequestException: handlers.bad_request_handler,
    ExternalServiceException: handlers.external_service_exception_handler,
    404: handlers.not_found_error,
}
