from dependency_injector.wiring import inject, Provide

from app.schemas.llm_schema import (
    LlmDTO,
    convert_llm_to_llm_dto,
    convert_llm_dto_to_llm,
)
from app.repository import LlmCrud
from app.database.rdb import Transactional, Propagation
from app.cores.constants import SupportedModels
from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode
import bcrypt

class LlmService:
    @inject
    def __init__(self, llm_crud: LlmCrud) -> None:
        self.llm_crud = llm_crud
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def create_llm(self, user_id: str, llm_dto: LlmDTO) -> LlmDTO:        
        if (await self.llm_crud.get_llm(user_id, llm_dto.llm_name, llm_dto.llm_type) is not None):
            raise InvalidRequestException("llm_name", error_code=ErrorCode.DUPLICATED_VALUE)
        elif llm_dto.llm_type != SupportedModels.LLM.get(llm_dto.llm_name, None):
            raise InvalidRequestException("llm_type", error_code=ErrorCode.NOT_EXIST)
        
        llm_dto.create_user_id = llm_dto.modified_user_id = user_id

        llm = convert_llm_dto_to_llm(llm_dto)
        llm = await self.llm_crud.save(llm=llm)
        return convert_llm_to_llm_dto(llm)
    
    async def get_llms(self, user_id: str | None) -> list[LlmDTO]:
        if user_id == "admin":  # TODO : admin 계정에 대한 공통 식별 방법
            llms = await self.llm_crud.get_all_llms()
        else:
            llms = await self.llm_crud.get_user_llms(user_id)
        return [convert_llm_to_llm_dto(llm) for llm in llms]
    
    async def get_llm(self, user_id: str, llm_name: str) -> LlmDTO:
        llm_type = SupportedModels.LLM.get(llm_name, None)

        if llm_type is None:
            raise InvalidRequestException("llm_model", error_code=ErrorCode.NOT_EXIST)

        llm = await self.llm_crud.get_llm(user_id, llm_name, llm_type, deleted=False)
        return convert_llm_to_llm_dto(llm)
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_llm(self, user_id: str, llm_name: str, llm_type: str) -> LlmDTO:
        delete_llm = await self.llm_crud.get_llm(user_id, llm_name, llm_type, deleted=False)

        await self.llm_crud.delete_llm(user_id, delete_llm)

        deleted_llm_DTO = convert_llm_to_llm_dto(delete_llm) if delete_llm else None
        return deleted_llm_DTO