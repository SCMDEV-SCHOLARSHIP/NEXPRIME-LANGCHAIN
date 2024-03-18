from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel

from .exceptions import InvalidRequestException, ExternalServiceException, HTTPException, ErrorCode


def get_error_schema(status_code:int , value:str ,error_code: ErrorCode) -> JSONResponse:
    return JSONResponse(
        content={
            "code": error_code.value[0],
            "message": f"{value} : {error_code.value[1]}",
        },
        status_code=status_code,
    )

async def bad_request_handler(
    request: Request, exc: InvalidRequestException
) -> JSONResponse:
    return get_error_schema(exc.status_code, exc.value, exc.error_code)


async def external_service_exception_handler(
    request: Request, exc: ExternalServiceException
) -> JSONResponse:
    return get_error_schema(exc.status_code, exc.value, exc.error_code)


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
