from pathlib import Path
import hashlib
from typing import Any, overload, Callable

from fastapi import Security
from fastapi.security import APIKeyHeader
from fastapi.requests import Request

from app.cores.exceptions.exceptions import InternalServerException
from app.cores.exceptions.error_code import ErrorCode


def as_posix(*paths: str) -> str:
    return Path().joinpath(*paths).as_posix()


def gen_id(src: str, len: int = 12) -> int:
    hash_id = str(int(hashlib.md5(src.encode()).hexdigest(), 16))
    try:
        lim_id = int(hash_id[:len])
    except:
        lim_id = int(hash_id)
    return lim_id


HEADERS = {
    "AT": Security(APIKeyHeader(name="Authorization", scheme_name="Access Token")),
    "RT": Security(APIKeyHeader(name="refresh_token", scheme_name="Refresh Token")),
}


@overload
def get_payload_info(request: Request, key: None = None) -> dict[str, Any]: ...


@overload
def get_payload_info(request: Request, key: str) -> Any: ...


def get_payload_info(request: Request, key: str | None = None) -> dict[str, Any] | Any:
    payload: dict[str, Any] = request.state.payload
    if key is None:
        return payload
    elif key not in payload:  # 코딩 에러
        raise InternalServerException(
            f"key '{key}' not in payload", ErrorCode.INTERNAL_SERVER_ERROR
        )
    return payload[key]


def same_as(column_name: str) -> Callable:
    def default_function(context):
        return context.current_parameters.get(column_name)

    return default_function
