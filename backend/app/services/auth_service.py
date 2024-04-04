from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime, timedelta, UTC

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Aggregate

from app.cores.exceptions.error_code import ErrorCode
from app.cores.exceptions.exceptions import (
    UnauthorizedException,
    InternalServerException,
)

from app.schemas.auth_schema import (
    JWTTokenDTO,
    convert_token_dto_to_token,
)
from app.repository import JWTTokenCrud
from app.database.rdb import Transactional, Propagation


class AuthService:  # 토큰 발행, 검증
    @inject
    def __init__(
        self,
        token_crud: JWTTokenCrud,
        secret_key: str = Provide["config.auth.secret_key"],
        algo: str = Provide["config.auth.algorithm"],
        strategy_aggregate: Aggregate[TokenValidationStrategy] = Provide[
            "token_validation_strategy.provider"
        ],
    ) -> None:
        self.token_crud = token_crud
        self.secret_key = secret_key
        self.algo = algo
        self.validation_mapping: dict[str, TokenValidationStrategy] = {
            validation_type: strategy()
            for validation_type, strategy in strategy_aggregate.providers.items()
        }

    def get_strategy(self, validation_type: str) -> TokenValidationStrategy:
        strategy = self.validation_mapping.get(validation_type, None)
        if strategy is None:  # 코딩 에러
            raise InternalServerException(
                "token_validation_type", ErrorCode.INTERNAL_SERVER_ERROR
            )
        return strategy

    @Transactional(propagation=Propagation.REQUIRED)
    async def save_token(self, token_dto: JWTTokenDTO) -> None:
        db_token = await self.token_crud.get_token(token_dto.user_id)
        if db_token is None:
            db_token = convert_token_dto_to_token(token_dto)
            await self.token_crud.save(db_token)
        else:
            db_token.refresh_token = token_dto.refresh_token
            db_token.delete_yn = False
            db_token.modified_datetime = datetime.now()
            db_token.modified_user_id = token_dto.user_id

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_token(self, user_id: str) -> bool:
        db_token = await self.token_crud.get_token(user_id)
        if db_token is None:
            return False
        db_token.delete_yn = True
        db_token.modified_datetime = datetime.now()
        db_token.modified_user_id = user_id
        return True

    @inject
    def make_token(
        self,
        sub: str,
        exp: int,
        iss: str = Provide["config.auth.issuer"],
        **extra_claims,
    ) -> str:
        base_claims = {"iss": iss, "sub": sub, "exp": exp}
        base_claims.update(extra_claims)
        return jwt.encode(base_claims, self.secret_key, self.algo)

    async def issue_renewal_tokens(self, token_dto: JWTTokenDTO) -> dict[str, Any]:
        access_token_user_id: str = token_dto.user_id
        claims = self.get_strategy("default").validate(token_dto.refresh_token)
        refresh_token_user_id: str = claims["sub"]

        if access_token_user_id != refresh_token_user_id:
            raise UnauthorizedException("token_user_id", ErrorCode.NOT_MATCHED_VALUE)

        db_token = await self.token_crud.get_token(token_dto.user_id)
        if (
            db_token is None
            or db_token.refresh_token != token_dto.refresh_token
            or db_token.delete_yn == True
        ):
            raise UnauthorizedException("refresh_token", ErrorCode.NOT_EXIST)
        return self.issue_new_tokens(refresh_token_user_id)

    @inject
    def issue_new_tokens(
        self,
        user_id: str,
        access_token_config: dict[str, Any] = Provide["config.auth.access_token"],
        refresh_token_config: dict[str, Any] = Provide["config.auth.refresh_token"],
    ) -> dict[str, Any]:
        issued_at = datetime.now(UTC)
        access_exp = issued_at + timedelta(
            minutes=access_token_config["expire_minutes"]
        )
        refresh_exp = issued_at + timedelta(
            minutes=refresh_token_config["expire_minutes"]
        )

        new_access_token = self.make_token(
            sub=user_id,
            exp=access_exp,
        )

        new_refresh_token = self.make_token(
            sub=user_id,
            exp=refresh_exp,
            nbf=access_exp,
        )

        return {
            "user_id": user_id,
            "token_type": "Bearer",
            "access_token": new_access_token,
            "expires_at": access_exp,
            "refresh_token": new_refresh_token,
            "refresh_token_expires_at": refresh_exp,
        }


class TokenValidationStrategy(ABC):
    @inject
    def __init__(
        self,
        secret_key: str = Provide["config.auth.secret_key"],
        algo: str = Provide["config.auth.algorithm"],
        iss: str = Provide["config.auth.issuer"],
    ) -> None:
        self.secret_key = secret_key
        self.algo = algo
        self.iss = iss

    @abstractmethod
    def validate(self, token: str, *args, **kwargs) -> dict[str, Any]: ...


class DefaultValidationStrategy(TokenValidationStrategy):
    def validate(self, token: str) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                self.algo,
                issuer=self.iss,
                options={"require_iss": True, "require_sub": True, "require_exp": True},
            )
            return claims
        except ExpiredSignatureError:
            raise UnauthorizedException("token", ErrorCode.EXPIRED)
        except (JWTError, JWTClaimsError):
            raise UnauthorizedException("token", ErrorCode.INVALID_FORMAT)


# TODO: 사용 안하면 삭제
class IgnoreExpiredValidationStrategy(TokenValidationStrategy):
    def validate(self, token: str) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                self.algo,
                issuer=self.iss,
                options={"verify_exp": False},
            )
            return claims
        except (JWTError, JWTClaimsError):
            raise UnauthorizedException("token", ErrorCode.INVALID_FORMAT)


class ExpiredYetValidationStrategy(TokenValidationStrategy):
    def validate(self, token: str) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                self.algo,
                issuer=self.iss,
                options={"verify_exp": False},
            )
            if claims["exp"] > datetime.now(UTC).timestamp():
                raise UnauthorizedException("token", ErrorCode.NOT_EXPIRED)
            return claims
        except (JWTError, JWTClaimsError):
            raise UnauthorizedException("token", ErrorCode.INVALID_FORMAT)
