from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.models.llm import Llm

class LlmDTO(BaseModel, extra="forbid"):
    llm_type: Literal["sds", "openai"]
    llm_name: str
    inference_server_url: str | None = None
    max_new_tokens: Optional[int]
    top_k: Optional[int]
    top_p: Optional[float]
    typical_p: Optional[float]
    temperature: Optional[float]
    repetition_penalty: Optional[float]
    api_key: str | None = None
    streaming: Optional[bool]
    create_datetime: datetime | None = None
    create_user_id: str | None = None
    modified_datetime: datetime | None = None
    modified_user_id: str | None = None

    @validator("llm_name")
    def validate_llm_name(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("llm_name", error_code=ErrorCode.NOT_EXIST)
        return value
    
    @validator("inference_server_url")
    def validate_llm_url(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("inference_server_url", error_code=ErrorCode.NOT_EXIST)
        return value
    
def convert_llm_to_llm_dto(llm: Llm | None) -> LlmDTO | None:
    if llm is None:
        return llm
    llm_dict: dict = llm.__dict__
    llm_dict.pop("llm_id", None)
    llm_dict.pop("delete_yn", None)
    llm_dict.pop("_sa_instance_state", None)
    return LlmDTO(**llm_dict)

def convert_llm_dto_to_llm(llm_dto: LlmDTO) -> Llm:
    llm_dict: dict = llm_dto.__dict__
    return Llm(**llm_dict)