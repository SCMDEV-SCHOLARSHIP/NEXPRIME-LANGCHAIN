from app.schemas.user_schema import (
    UserDTO,
    convert_user_to_user_dto,
    convert_user_dto_to_user,
)
from dependency_injector.wiring import inject
from app.repository import UserCrud
from app.database.rdb import Transactional, Propagation
from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode


class UserService:

    @inject
    def __init__(self, user_crud: UserCrud):
        self.user_crud = user_crud

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_user(self, user_dto: UserDTO) -> UserDTO:
        if await self.user_crud.get_user(user_dto.user_id) != None:
            raise InvalidRequestException(
                "user_id",
                ErrorCode(code="KMG_ERROR_R_002", message="user_id is duplicated"),
            )

        user = convert_user_dto_to_user(user_dto)

        user = await self.user_crud.save(user=user)
        return convert_user_to_user_dto(user)

    async def get_users(self) -> list[UserDTO]:
        users = await self.user_crud.get_users()
        user_dtos = []
        for user in users:
            user_dtos.append(convert_user_to_user_dto(user))

        return user_dtos
