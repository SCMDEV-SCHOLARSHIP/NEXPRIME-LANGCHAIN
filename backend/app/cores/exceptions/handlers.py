from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException

from .exceptions import (
    SDSHTTPException,
    InvalidRequestException,
    ForbiddenAccessException,
    InternalServerException,
    ExternalServiceException,
)


async def get_error_schema(exc: SDSHTTPException) -> JSONResponse:
    return JSONResponse(
        content={
            "code": exc.error_code.value[0],
            "message": f"{exc.value} : {exc.error_code.value[1]}",
        },
        status_code=exc.status_code,
    )


async def bad_request_handler(
    request: Request, exc: InvalidRequestException
) -> JSONResponse:
    return await get_error_schema(exc)


async def unauthorized_handler(
    request: Request, exc: InvalidRequestException
) -> JSONResponse:
    return await get_error_schema(exc)


async def forbidden_access_handler(
    request: Request, exc: ForbiddenAccessException
) -> JSONResponse:
    return await get_error_schema(exc)


async def internal_server_exception_handler(
    request: Request, exc: InternalServerException
) -> JSONResponse:
    return await get_error_schema(exc)


async def external_service_exception_handler(
    request: Request, exc: ExternalServiceException
) -> JSONResponse:
    return await get_error_schema(exc)


# TODO: 예시 코드 -> 나중에 삭제
async def not_found_error(request: Request, exc: HTTPException) -> HTMLResponse:
    return HTMLResponse(
        status_code=404,
        content=f"""
        <html>

        <head>
            <title>404 Not Found</title>
        </head>

        <body style="padding: 30px">
            <h1>404 Not Found</h1>
            <p>The resource could not be found.</p>
        </body>

        </html>
        """,
    )
