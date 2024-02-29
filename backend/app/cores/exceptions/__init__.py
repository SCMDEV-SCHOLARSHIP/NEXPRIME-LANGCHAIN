from collections.abc import Callable, Coroutine
from typing import Any
from fastapi import Request, Response

from .exceptions import ValueNotExistException, HTTPException
from app.cores.exceptions import handlers


EXC_HDLRs: dict[
    int | type[Exception], Callable[[Request, Exception], Coroutine[Any, Any, Response]]
] = {
    ValueNotExistException: handlers.value_not_exist_handler,
    500: handlers.http_exception_handler,
    404: handlers.not_found_error,
}
