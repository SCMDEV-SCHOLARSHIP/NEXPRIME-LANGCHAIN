from dependency_injector.wiring import inject, Provide

from app.schemas.llm_schema import (
    LlmDTO,
    convert_llm_to_llm_dto,
    convert_llm_dto_to_llm,
)
from app.repository import LlmCrud

class LlmService:
    @inject
    def __init__(self, llm_crud: LlmCrud) -> None:
        self.llm_crud = llm_crud
    
    async def get_llms(self) -> list[LlmDTO]:
        llms = await self.llm_crud.get_llms()
        return [convert_llm_to_llm_dto(llm) for llm in llms]