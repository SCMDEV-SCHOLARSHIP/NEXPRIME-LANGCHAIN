from sqlalchemy import select, update, and_, values
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide

from app.models.llm import Llm

class LlmCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session
    
    async def get_all_llms(self, deleted: bool = False) -> list[Llm]:   # for admin
        query = select(Llm)
        if not deleted:
            query = query.where(Llm.delete_yn == False)
        llms = await self.session.execute(query)
        return llms.scalars().all()
    
    async def get_user_llms(self, user_id: str, deleted: bool = False) -> list[Llm]:
        query = select(Llm).where(Llm.create_user_id == user_id)
        if not deleted:
            query = query.where(Llm.delete_yn == False)
        llms = await self.session.execute(query)
        return llms.scalars().all()

    async def save(self, llm: Llm) -> Llm:
        self.session.add(llm)
        return llm
    
    async def get_llm(self, user_id: str, llm_type: str, llm_name: str, deleted: bool = False) -> Llm | None:
        query = select(Llm).where(
            and_(
                Llm.create_user_id == user_id,
                Llm.llm_type == llm_type,
                Llm.llm_name == llm_name,
            )
        )
        if not deleted: # TODO : delete에 대한 공통 logic 구현 필요
            query = query.where(Llm.delete_yn == False)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def delete_llm(self, user_id: str, llm: Llm) -> Llm:
        query = update(Llm).where(
            and_(
                Llm.create_user_id == user_id,
                Llm.llm_type == llm.llm_type,
                Llm.llm_name == llm.llm_name,
            )
        ).values({Llm.delete_yn : True})
        await self.session.execute(query)
        return llm