from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exception_handlers import http_exception_handler

from .exceptions import ValueNotExistException, HTTPException


async def value_not_exist_handler(
    request: Request, exc: ValueNotExistException
) -> JSONResponse:  # example: custom exception
    return JSONResponse(
        content={"detail": exc.detail},
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
