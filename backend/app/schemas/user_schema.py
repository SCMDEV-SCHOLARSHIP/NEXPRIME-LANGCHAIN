from pydantic import BaseModel, Field
from app.models.user import User
from typing import Dict, Optional
from datetime import datetime


class UserDTO(BaseModel, extra="forbid"):
    user_id: str
    user_name: str
    user_email: str
    create_datetime: Optional[datetime] = Field(default=None)
    create_user_id: Optional[str] = Field(default=None)
    modified_datetime: Optional[datetime] = Field(default=None)
    modified_user_id: Optional[str] = Field(default=None)


def convert_user_to_user_dto(user: User) -> UserDTO:
    user_dict: Dict = user.__dict__
    del user_dict["_sa_instance_state"]
    return UserDTO(**user_dict)


def convert_user_dto_to_user(user_dto: UserDTO) -> User:
    user_dict: Dict = user_dto.__dict__
    return User(**user_dict)
