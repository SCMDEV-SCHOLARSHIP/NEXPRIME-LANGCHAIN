from pydantic import BaseModel
from datetime import datetime

from app.models.token import JWTToken


class JWTTokenIssueRequest(BaseModel):
    user_id: str
    verify_code: str


class JWTTokenIssueResponse(BaseModel):
    user_id: str
    access_token: str
    expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime


class JWTTokenDTO(BaseModel):
    user_id: str
    refresh_token: str


def convert_token_to_token_dto(token: JWTToken) -> JWTTokenDTO:
    token_dict = token.__dict__
    del token_dict["_sa_instance_state"]
    return JWTTokenDTO(**token_dict)


def convert_token_dto_to_token(token_dto: JWTTokenDTO) -> JWTToken:
    token_dict = token_dto.__dict__
    return JWTToken(**token_dict)
