import re
from typing import Callable, Coroutine, Any
from starlette.types import ASGIApp
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.cores.exceptions.error_code import ErrorCode
from app.cores.exceptions.handlers import forbidden_access_handler
from app.cores.exceptions.exceptions import ForbiddenAccessException


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        token_validator: Callable[[str], Coroutine[Any, Any, dict[str, Any]]],
        excluded_paths: set[str] = {"/", "/openapi.json", "/auth/token"},
        excluded_paths_regex: str = "^(/docs|/redoc)",
    ) -> None:
        super().__init__(app)
        self.token_validator = token_validator
        self.excluded_paths = excluded_paths
        self.exclueded_regex = excluded_paths_regex

    async def check_path_pattern(self, path: str, pattern: str) -> bool:
        result = re.match(pattern, path)
        if result:
            return True
        return False

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[Any, Any, Response]],
    ) -> Response:
        url_path = request.url.path
        if not (
            await self.check_path_pattern(url_path, self.exclueded_regex)
            or url_path in self.excluded_paths
        ):
            try:
                credentials = await HTTPBearer()(request)
            except HTTPException:
                return await forbidden_access_handler(
                    request,
                    ForbiddenAccessException("Header", ErrorCode.INVALID_FORMAT),
                )
            token = credentials.credentials
            if url_path == "/auth/renewal":
                request.state.access_token = token
            else:
                try:
                    await self.token_validator(token)
                # token_validator에 다른 exception 발생 시 추가할 것
                except ForbiddenAccessException as e:
                    return await forbidden_access_handler(request, e)
        response = await call_next(request)
        return response
