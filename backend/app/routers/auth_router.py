from fastapi import APIRouter, status, Depends, Request, Security
from fastapi.security import APIKeyHeader
from dependency_injector.wiring import inject, Provide

from app.cores.exceptions.error_code import ErrorCode
from app.cores.exceptions.exceptions import UnauthorizedException

from app.cores.di_container import DiContainer
import app.schemas.auth_schema as schema
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth")


@router.post(
    "/refresh",
    response_model=schema.JWTTokenIssueResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def issue_renewal_tokens(
    request: Request,
    auth_service: AuthService = Depends(Provide[DiContainer.auth_service]),
) -> schema.JWTTokenIssueResponse:
    access_token: str = request.state.access_token
    del request.state.access_token

    refresh_token = request.headers.get("refresh_token")
    if refresh_token is None:
        raise UnauthorizedException("Header", ErrorCode.INVALID_FORMAT)

    claims = auth_service.get_strategy("expired_yet").validate(access_token)

    token_dto = schema.JWTTokenDTO(user_id=claims["sub"], refresh_token=refresh_token)
    token_results = await auth_service.issue_renewal_tokens(token_dto)
    response = schema.JWTTokenIssueResponse(**token_results)
    token_dto = schema.JWTTokenDTO(
        user_id=response.user_id, refresh_token=response.refresh_token
    )
    await auth_service.save_token(token_dto)
    return response
