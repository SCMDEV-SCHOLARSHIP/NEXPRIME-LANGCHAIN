from fastapi import APIRouter, status
from app.schemas.user_schema import UserDTO
from app.services.user_service import UserService

router = APIRouter(prefix="/users")


@router.post(
    "/",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
)
async def create_user(user_dto: UserDTO) -> UserDTO:

    ret_user = await UserService().create_user(user_dto)
    return ret_user


@router.get(
    "/",
    response_model=list[UserDTO],
    status_code=status.HTTP_200_OK,
    summary="Get All Users",
)
async def get_users() -> list[UserDTO]:

    ret_user = await UserService().get_users()
    return ret_user
