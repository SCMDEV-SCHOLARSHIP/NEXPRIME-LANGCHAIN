import re
from typing import Callable, Coroutine, Any
from starlette.types import ASGIApp
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        token_validator: Callable[
            [str], Coroutine[Any, Any, Any]
        ],  # TODO: 리턴 타입 지정
        excluded_paths: set[str] = {"/", "/openapi.json"},
        excluded_paths_regex: str = "^(/docs|/redoc|/auth)",
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
            except HTTPException as e:  # TODO: 토큰 없음 예외 처리
                return JSONResponse({e.status_code: e.detail})
            token = credentials.credentials
            await self.token_validator(token)  # TODO: 에러 response면 여기서 반환
        response = await call_next(request)
        return response
