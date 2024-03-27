from sqlalchemy import select

from app.models.token import JWTToken
from app.database.rdb import session


class JWTTokenCrud:
    async def get_tokens(self) -> list[JWTToken]:
        query = await session.execute(select(JWTToken))
        return query.scalars().all()

    async def save(self, token: JWTToken) -> None:
        token.create_user_id = token.user_id
        token.modified_user_id = token.user_id
        session.add(token)
        return

    async def get_token(self, user_id: str) -> JWTToken:
        query = select(JWTToken).where(JWTToken.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def delete(self, token: JWTToken) -> None:
        db_token = await self.get_token(token)
        if db_token:
            await session.delete(db_token)
