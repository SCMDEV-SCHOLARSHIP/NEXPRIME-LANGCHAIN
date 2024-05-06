from sqlalchemy import select, and_
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

    async def save(self, llm: Llm) -> Llm:
        self.session.add(llm)
        return llm
    
    async def get_llm(self, llm: Llm) -> Llm | None:
        query = select(Llm).where(
            and_(
                Llm.llm_type == llm.llm_type,
                Llm.llm_name == llm.llm_name,
                Llm.create_user_id == llm.create_user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()