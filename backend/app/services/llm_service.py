from dependency_injector.wiring import inject, Provide

from app.schemas.llm_schema import (
    LlmDTO,
    convert_llm_to_llm_dto,
    convert_llm_dto_to_llm,
)
from app.repository import LlmCrud
from app.database.rdb import Transactional, Propagation
from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode
import bcrypt

class LlmService:
    @inject
    def __init__(self, llm_crud: LlmCrud) -> None:
        self.llm_crud = llm_crud
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def create_llm(self, llm_dto: LlmDTO) -> LlmDTO:        
        if llm_dto.api_key:
            llm_dto.api_key = bcrypt.hashpw(llm_dto.api_key.encode(), bcrypt.gensalt()).decode("utf-8")
        
        llm = convert_llm_dto_to_llm(llm_dto)

        if (await self.llm_crud.get_llm(llm) is not None):
            raise InvalidRequestException("llm_name", error_code=ErrorCode.DUPLICATED_VALUE)

        llm = await self.llm_crud.save(llm=llm)
        return convert_llm_to_llm_dto(llm)
    
    async def get_llms(self) -> list[LlmDTO]:
        llms = await self.llm_crud.get_llms()
        return [convert_llm_to_llm_dto(llm) for llm in llms]