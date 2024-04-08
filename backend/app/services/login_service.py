from __future__ import annotations
from abc import ABC, abstractmethod
import bcrypt

from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Aggregate

from app.cores.exceptions import InvalidRequestException, UnauthorizedException
from app.cores.exceptions.error_code import ErrorCode

import app.schemas.login_schema as schema
from app.repository.user_crud import UserCrud


class LoginService:  # 비밀번호 검증 + user 확인 로직
    @inject
    def __init__(
        self,
        strategy_aggregate: Aggregate[LoginStrategy] = Provide[
            "login_strategy.provider"
        ],
    ) -> None:
        self.login_mapping: dict[str, LoginStrategy] = {
            login_type: strategy()
            for login_type, strategy in strategy_aggregate.providers.items()
        }

    def get_strategy(self, login_type: str) -> LoginStrategy:
        strategy = self.login_mapping.get(login_type, None)
        if strategy is None:
            raise InvalidRequestException("login_type", ErrorCode.BAD_REQUEST)
        return strategy

    def check_password_match(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class LoginStrategy(ABC):
    @abstractmethod
    async def login(self, login_dto: schema.LoginDTO, *args, **kwargs) -> None: ...

    def check_password_match(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class FormBaseLoginStrategy(LoginStrategy):
    @inject
    async def login(
        self, login_dto: schema.LoginDTO, user_crud: UserCrud = Provide["user_crud"]
    ) -> None:
        db_user = await user_crud.get_user(login_dto.user_id)
        if db_user is None:
            raise UnauthorizedException("user_id", ErrorCode.BAD_REQUEST)
        if not self.check_password_match(
            login_dto.user_password, db_user.user_password
        ):
            raise UnauthorizedException("user_password", ErrorCode.BAD_REQUEST)
        return
