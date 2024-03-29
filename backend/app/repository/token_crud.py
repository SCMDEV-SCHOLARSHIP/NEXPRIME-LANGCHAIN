from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide

from app.models.token import JWTToken


class JWTTokenCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session

    async def get_tokens(self) -> list[JWTToken]:
        query = await self.session.execute(select(JWTToken))
        return query.scalars().all()

    async def save(self, token: JWTToken) -> None:
        token.create_user_id = token.user_id
        token.modified_user_id = token.user_id
        self.session.add(token)
        return

    async def get_token(self, user_id: str) -> JWTToken:
        query = select(JWTToken).where(JWTToken.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete(self, token: JWTToken) -> None:
        db_token = await self.get_token(token)
        if db_token:
            await self.session.delete(db_token)
