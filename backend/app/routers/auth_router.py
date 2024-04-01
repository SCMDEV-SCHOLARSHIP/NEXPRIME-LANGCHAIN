import bcrypt
from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide
from logging import Logger

from app.cores.exceptions.error_code import ErrorCode
from app.cores.exceptions.exceptions import (
    UnauthorizedException,
    InternalServerException,
)

from app.cores.di_container import DiContainer
import app.schemas.auth_schema as schema
from app.services.auth_service import AuthService
from app.services.user_service import UserService
import datetime

router = APIRouter(prefix="/auth")


@router.post(
    "/token",
    response_model=schema.JWTTokenIssueResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def issue_new_tokens(
    token_req: schema.JWTTokenIssueRequest,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
) -> schema.JWTTokenIssueResponse:
    if token_req.verify_code == "test":  # TODO: 인증 코드 검사 로직
        result = await auth_service.issue_new_tokens(token_req.user_id)
        response = schema.JWTTokenIssueResponse(**result)
        token_dto = schema.JWTTokenDTO(
            user_id=response.user_id, refresh_token=response.refresh_token
        )
        await auth_service.save_token_in_db(token_dto)
        return response
    else:
        raise ValueError(token_req.verify_code)


@router.post(
    "/renewal",
    response_model=schema.JWTTokenIssueResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def issue_renewal_tokens(
    request: Request,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
    logger: Logger = Depends(Provide["logger"]),
) -> schema.JWTTokenIssueResponse:
    access_token: str = request.state.access_token
    del request.state.access_token
    checking_expired_task = auth_service.check_expired(access_token)

    refresh_token = request.headers.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Header", ErrorCode.NOT_EXIST)

    expired, claims = await checking_expired_task
    if not expired:
        raise UnauthorizedException("token", ErrorCode.NOT_EXPIRED)
    try:
        assert claims is not None
    except:
        logger.error("Assertion Failed: {claims} is None")
        raise InternalServerException("token claims", ErrorCode.INTERNAL_SERVER_ERROR)

    token_dto = schema.JWTTokenDTO(user_id=claims["sub"], refresh_token=refresh_token)
    result = await auth_service.issue_renewal_tokens(token_dto)
    response = schema.JWTTokenIssueResponse(**result)

    token_dto = schema.JWTTokenDTO(
        user_id=response.user_id, refresh_token=response.refresh_token
    )
    await auth_service.save_token_in_db(token_dto)
    return response

@router.post(
    "/login",
    response_model=schema.JWTTokenIssueResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    login_dto: schema.LoginDTO,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
    user_service: UserService = Depends(Provide[DiContainer.user_service]),
) -> schema.JWTTokenIssueResponse:
    user_dto = await user_service.get_user(login_dto.user_id)

    if not auth_service.check_password_match(login_dto.user_password, user_dto.user_password):
        raise UnauthorizedException("user_password", ErrorCode.BAD_REQUEST)

    #TODO: issue token logic
    token = "issue token!!"
    now = datetime.datetime.now()
    user_id = user_dto.user_id
    return schema.JWTTokenIssueResponse(**{
        "user_id": user_id,
        "access_token": token,
        "expires_at": now,
        "refresh_token": token,
        "refresh_token_expires_at": now,
    })
