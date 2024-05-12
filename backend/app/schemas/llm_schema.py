from pydantic import BaseModel, model_validator
from typing import Optional, Any
from datetime import datetime

from app.cores.constants import SupportedModels
from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.models.llm import Llm

class LlmDTO(BaseModel, extra="forbid"):
    llm_type: str
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

    @model_validator(mode="before")
    def validate_llm_name(self, data: Any):
        if isinstance(data, dict):
            llm_name = data.get("llm_name")
            llm_type = data.get("llm_type")
            
            if not llm_name or len(llm_name) == 0:
                raise InvalidRequestException("llm_name", error_code=ErrorCode.NOT_EXIST)
            supported_type = SupportedModels.LLM.get(llm_name, None)
            if supported_type is None:
                raise InvalidRequestException("llm_name", error_code=ErrorCode.BAD_REQUEST)
            elif supported_type != llm_type:
                raise InvalidRequestException("llm_type", error_code=ErrorCode.BAD_REQUEST)
        return self
    
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