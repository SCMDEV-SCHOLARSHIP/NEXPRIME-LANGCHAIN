import asyncio
from typing import Any
from datetime import datetime, timedelta, UTC
from jose import jwt
from pydantic import SecretStr
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from dependency_injector.wiring import inject, Provide

from app.cores.exceptions.error_code import ErrorCode
from app.cores.exceptions.exceptions import UnauthorizedException

from app.cores.config import ConfigContianer
from app.schemas.auth_schema import (
    JWTTokenDTO,
    convert_token_dto_to_token,
)
from app.repository import JWTTokenCrud
from app.database.rdb import Transactional, Propagation


class AuthService:
    @inject
    def __init__(
        self,
        token_crud: JWTTokenCrud,
        secret_key: SecretStr = Provide[ConfigContianer.config.auth.secret_key],
        algo: str = Provide[ConfigContianer.config.auth.algorithm],
    ) -> None:
        self.token_crud = token_crud
        self.secret_key = secret_key.get_secret_value()
        self.algo = algo

    @inject
    async def make_claims(
        self,
        sub: str,
        exp: int,
        iss: str = Provide[ConfigContianer.config.auth.issuer],
        **extra_claims,
    ) -> dict[str, Any]:
        base_claims = {"iss": iss, "sub": sub, "exp": exp}
        base_claims.update(extra_claims)
        return base_claims

    async def make_token(self, claims: dict[str, Any]) -> str:
        return jwt.encode(claims, self.secret_key, self.algo)

    @inject
    async def check_expired(
        self, token: str, iss: str = Provide[ConfigContianer.config.auth.issuer]
    ) -> tuple[bool, dict[str, Any] | None]:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                self.algo,
                issuer=iss,
                options={"verify_exp": False},
            )
            if claims["exp"] <= datetime.now(UTC).timestamp():
                return True, claims
        except (JWTError, JWTClaimsError):
            raise UnauthorizedException("token", ErrorCode.INVALID_FORMAT)
        return False, None

    @inject
    async def validate_token(
        self, token: str, iss: str = Provide[ConfigContianer.config.auth.issuer]
    ) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                self.algo,
                issuer=iss,
                options={"require_iss": True, "require_sub": True, "require_exp": True},
            )
            return claims
        except ExpiredSignatureError:
            raise UnauthorizedException("token", ErrorCode.EXPIRED)
        except (JWTError, JWTClaimsError):
            raise UnauthorizedException("token", ErrorCode.INVALID_FORMAT)

    async def check_token_in_db(self, token_dto: JWTTokenDTO) -> bool:
        db_token = await self.token_crud.get_token(token_dto.user_id)
        if not db_token or db_token.refresh_token != token_dto.refresh_token:
            return False
        return True

    @Transactional(propagation=Propagation.REQUIRED)
    async def save_token_in_db(self, token_dto: JWTTokenDTO) -> None:
        db_token = await self.token_crud.get_token(token_dto.user_id)
        if db_token:
            db_token.refresh_token = token_dto.refresh_token
            return
        else:
            db_token = convert_token_dto_to_token(token_dto)
            return await self.token_crud.save(db_token)

    async def delete_token_in_db(self, token_dto: JWTTokenDTO) -> None:
        db_token = await convert_token_dto_to_token(token_dto)
        return await self.token_crud.delete(db_token)

    async def issue_renewal_tokens(self, token_dto: JWTTokenDTO) -> dict[str, Any]:
        access_token_user_id: str = token_dto.user_id
        claims = await self.validate_token(token_dto.refresh_token)
        refresh_token_user_id: str = claims["sub"]

        if access_token_user_id != refresh_token_user_id:
            raise UnauthorizedException("token_user_id", ErrorCode.NOT_MATCHED_VALUE)

        if await self.check_token_in_db(token_dto):
            return await self.issue_new_tokens(refresh_token_user_id)
        else:
            raise UnauthorizedException("refresh_token", ErrorCode.NOT_EXIST)

    @inject
    async def issue_new_tokens(
        self,
        user_id: str,
        access_token_expire_minutes: int = Provide[
            ConfigContianer.config.auth.access_token_expire_minutes
        ],
        refresh_token_expire_minutes: int = Provide[
            ConfigContianer.config.auth.refresh_token_expire_minutes
        ],
    ) -> dict[str, Any]:
        issued_at = datetime.now(UTC)
        access_exp = issued_at + timedelta(minutes=access_token_expire_minutes)
        refresh_exp = issued_at + timedelta(minutes=refresh_token_expire_minutes)

        access_claims, refresh_claims = await asyncio.gather(
            self.make_claims(
                sub=user_id,
                exp=access_exp,
            ),
            self.make_claims(
                sub=user_id,
                exp=refresh_exp,
                nbf=access_exp,
            ),
        )
        new_access_token, new_refresh_token = await asyncio.gather(
            self.make_token(access_claims), self.make_token(refresh_claims)
        )

        return {
            "user_id": user_id,
            "access_token": new_access_token,
            "expires_at": access_exp,
            "refresh_token": new_refresh_token,
            "refresh_token_expires_at": refresh_exp,
        }
