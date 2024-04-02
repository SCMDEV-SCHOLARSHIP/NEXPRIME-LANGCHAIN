from fastapi import APIRouter, status, Depends
from app.schemas.user_schema import UserDTO
from dependency_injector.wiring import inject, Provide
from app.cores.di_container import DiContainer
from app.services.user_service import UserService

router = APIRouter(prefix="/users")


@router.post(
    "/sign-up",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
)
@inject
async def create_user(
    user_dto: UserDTO,
    user_service: UserService = Depends(Provide[DiContainer.user_service]),
) -> UserDTO:

    ret_user = await user_service.create_user(user_dto)
    return ret_user


@router.get(
    "/",
    response_model=list[UserDTO],
    status_code=status.HTTP_200_OK,
    summary="Get All Users",
)
@inject
async def get_users(
    user_service: UserService = Depends(Provide[DiContainer.user_service]),
) -> list[UserDTO]:

    ret_user = await user_service.get_users()
    return ret_user
