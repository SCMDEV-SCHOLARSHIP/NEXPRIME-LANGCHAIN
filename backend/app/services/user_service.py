import app.database.user_crud as user_crud
from app.schemas.user_schema import (
    UserDTO,
    convert_user_to_user_dto,
    convert_user_dto_to_user,
)


def get_user_list() -> list[UserDTO]:
    user_list = user_crud.get_user_list()
    ret_user_list = []
    for user in user_list:
        ret_user_list.append(convert_user_to_user_dto(user))

    return ret_user_list


def create_user(user_dto: UserDTO) -> UserDTO:
    user = convert_user_dto_to_user(user_dto)
    ret_user = user_crud.create_user(user)

    return convert_user_to_user_dto(ret_user)


def delete_user(user_dto: UserDTO) -> UserDTO:
    ret_user = user_crud.delete_user(user_dto.user_id)

    return convert_user_to_user_dto(ret_user)
