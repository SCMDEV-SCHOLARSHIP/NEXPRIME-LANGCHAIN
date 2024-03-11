from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel

from .exceptions import ValueNotExistException, InvalidRequestException, HTTPException


async def value_not_exist_handler(
    request: Request, exc: ValueNotExistException
) -> JSONResponse:  # example: custom exception
    return JSONResponse(
        content={"code": exc.detail.code, "message": exc.detail.message},
        status_code=exc.status_code,
    )


async def bad_request_handler(
    request: Request, exc: InvalidRequestException
) -> JSONResponse:
    return JSONResponse(
        content={"code": exc.detail.code, "message": exc.detail.message},
        status_code=exc.status_code,
    )


async def not_found_error(
    request: Request, exc: HTTPException
) -> HTMLResponse:  # example: global 404 exception
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
