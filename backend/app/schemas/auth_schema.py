from pydantic import BaseModel, validator
from datetime import datetime

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.models.token import JWTToken


class JWTTokenIssueResponse(BaseModel, extra="forbid"):
    user_id: str
    token_type: str
    access_token: str
    expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime


class JWTTokenDTO(BaseModel, extra="forbid"):
    user_id: str
    refresh_token: str
    create_datetime: datetime | None = None
    create_user_id: str | None = None
    modified_datetime: datetime | None = None
    modified_user_id: str | None = None

    @validator("user_id")
    def validate_user_id(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("user_id", error_code=ErrorCode.NOT_EXIST)
        return value


def convert_token_to_token_dto(token: JWTToken) -> JWTTokenDTO:
    token_dict = token.__dict__
    del token_dict["delete_yn"]
    del token_dict["_sa_instance_state"]
    return JWTTokenDTO(**token_dict)


def convert_token_dto_to_token(token_dto: JWTTokenDTO) -> JWTToken:
    token_dict = token_dto.__dict__
    return JWTToken(**token_dict)
