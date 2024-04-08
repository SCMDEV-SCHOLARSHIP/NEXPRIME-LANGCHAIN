from typing import Any
from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.cores.utils import HEADERS
from app.cores.di_container import DiContainer
import app.schemas.login_schema as schema
import app.schemas.auth_schema as auth_schema
from app.services.login_service import LoginService
from app.services.auth_service import AuthService


router = APIRouter(prefix="")


@router.post(
    "/login",
    response_model=auth_schema.JWTTokenIssueResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    login_req: schema.LoginRequest,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
    login_service: LoginService = Depends(Provide[DiContainer.login_service]),
) -> auth_schema.JWTTokenIssueResponse:
    login_dto = schema.LoginDTO(
        user_id=login_req.user_id, user_password=login_req.user_password
    )
    login_strategy = login_service.get_strategy(login_req.login_type)
    await login_strategy.login(login_dto)

    token_results = auth_service.issue_new_tokens(login_req.user_id)
    response = auth_schema.JWTTokenIssueResponse(**token_results)
    token_dto = auth_schema.JWTTokenDTO(
        user_id=response.user_id, refresh_token=response.refresh_token
    )
    await auth_service.save_token(token_dto)
    return response


@router.post(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[HEADERS["AT"]]
)
@inject
async def logout(
    request: Request,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
) -> None:
    payload: dict[str, Any] = request.state.payload
    user_id: str = payload["sub"]
    if await auth_service.delete_token(user_id) == False:
        raise InvalidRequestException("user_id", ErrorCode.BAD_REQUEST)
    return
