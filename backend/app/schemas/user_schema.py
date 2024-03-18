from pydantic import BaseModel, Field, validator
from app.models.user import User
from typing import Dict, Optional
from datetime import datetime
from app.cores.exceptions import InvalidRequestException
import re
from app.cores.exceptions.error_code import ErrorCode


class UserDTO(BaseModel, extra="forbid"):
    user_id: str
    user_name: str
    user_email: str
    create_datetime: Optional[datetime] = Field(default=None)
    create_user_id: Optional[str] = Field(default=None)
    modified_datetime: Optional[datetime] = Field(default=None)
    modified_user_id: Optional[str] = Field(default=None)

    @validator("user_id")
    def validate_user_id(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("user_id", error_code=ErrorCode.NOT_EXIST)
        return value

    @validator("user_email")
    def validate_user_email(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("user_email", error_code=ErrorCode.NOT_EXIST)

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        match = bool(re.match(pattern, value))
        if match == False:
            raise InvalidRequestException(
                "user_email", error_code=ErrorCode.INVALID_FORMAT
            )
        return value


def convert_user_to_user_dto(user: User) -> UserDTO:
    user_dict: Dict = user.__dict__
    del user_dict["_sa_instance_state"]
    return UserDTO(**user_dict)


def convert_user_dto_to_user(user_dto: UserDTO) -> User:
    user_dict: Dict = user_dto.__dict__
    return User(**user_dict)
