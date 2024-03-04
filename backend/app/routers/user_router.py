from fastapi import APIRouter, status
from app.models.user import User
from app.schemas.user_schema import UserDTO
import app.services.user_service as user_service

router = APIRouter(prefix="/users")


@router.get(
    "/",
    response_model=list[UserDTO],
    status_code=status.HTTP_200_OK,
)
def get_users() -> list[UserDTO]:

    return user_service.get_user_list()


@router.post(
    "/",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user_dto: UserDTO) -> UserDTO:

    ret_user = user_service.create_user(user_dto)
    return ret_user


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
)
def delete_user(user_dto: UserDTO) -> UserDTO:

    ret_user = user_service.delete_user(user_dto)
    return ret_user
