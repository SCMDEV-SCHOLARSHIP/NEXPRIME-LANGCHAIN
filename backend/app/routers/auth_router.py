from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide

from app.cores.di_container import DiContainer
import app.schemas.auth_schema as schema
from app.services.auth_service import AuthService

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
) -> schema.JWTTokenIssueResponse:
    access_token: str = request.state.access_token
    del request.state.access_token
    checking_expired_task = auth_service.check_expired(access_token)

    refresh_token = request.headers.get("refresh_token")
    if not refresh_token:
        raise Exception(refresh_token)  # TODO: 헤더 없음

    expired, claims = await checking_expired_task
    if not expired:  # TODO: 엑세스토큰 만료 X, 재발급 불가
        raise Exception("Not expired yet")
    assert claims is not None

    token_dto = schema.JWTTokenDTO(user_id=claims["sub"], refresh_token=refresh_token)
    result = await auth_service.issue_renewal_tokens(token_dto)
    response = schema.JWTTokenIssueResponse(**result)

    token_dto = schema.JWTTokenDTO(
        user_id=response.user_id, refresh_token=response.refresh_token
    )
    await auth_service.save_token_in_db(token_dto)
    return response
