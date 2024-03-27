from collections.abc import Callable, Coroutine
from typing import Any
from fastapi import Request, Response

from .exceptions import (
    InvalidRequestException,
    UnauthorizedException,
    ForbiddenAccessException,
    InternalServerException,
    ExternalServiceException,
)
from app.cores.exceptions import handlers


EXC_HDLRs: dict[
    int | type[Exception], Callable[[Request, Exception], Coroutine[Any, Any, Response]]
] = {
    InvalidRequestException: handlers.bad_request_handler,
    UnauthorizedException: handlers.unauthorized_handler,
    ForbiddenAccessException: handlers.forbidden_access_handler,
    InternalServerException: handlers.internal_server_exception_handler,
    ExternalServiceException: handlers.external_service_exception_handler,
    404: handlers.not_found_error,
}
