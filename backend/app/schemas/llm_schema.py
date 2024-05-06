from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.models.llm import Llm

class LlmDTO(BaseModel, extra="forbid"):
    llm_id: int
    llm_type: str
    llm_name: str
    llm_url: Optional[str]
    max_new_tokens: Optional[int]
    top_k: Optional[int]
    top_p: Optional[float]
    typical_p: Optional[float]
    temperature: Optional[float]
    repetition_penalty: Optional[float]
    api_key: Optional[str]
    streaming: Optional[bool]
    create_datetime: Optional[datetime] = Field(default=None)
    create_user_id: Optional[str] = Field(default=None)
    modified_datetime: Optional[datetime] = Field(default=None)
    modified_user_id: Optional[str] = Field(default=None)

    @validator("llm_name")
    def validate_llm_name(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("llm_name", error_code=ErrorCode.NOT_EXIST)
        return value
    
    @validator("llm_url")
    def validate_llm_url(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("llm_url", error_code=ErrorCode.NOT_EXIST)
        return value
    
def convert_llm_to_llm_dto(llm: Llm|None) -> LlmDTO:
    if llm is None:
        return llm
    llm_dict: dict = llm.__dict__
    del llm_dict["delete_yn"]
    del llm_dict["_sa_instance_state"]
    return LlmDTO(**llm_dict)

def convert_llm_dto_to_llm(llm_dto: LlmDTO) -> Llm:
    llm_dict: dict = llm_dto.__dict__
    return Llm(**llm_dict)