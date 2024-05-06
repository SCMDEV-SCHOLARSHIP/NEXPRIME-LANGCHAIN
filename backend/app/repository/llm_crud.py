from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide

from app.models.llm import Llm

class LlmCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session
    
    async def get_llms(self) -> list[Llm]:
        query = await self.session.execute(select(Llm))
        return query.scalars().all()

    # async def save(self, llm: Llm) -> Llm:
    #     self.session.add(llm)
    #     return await self.get_llm({"model_name": [llm.model_name]})