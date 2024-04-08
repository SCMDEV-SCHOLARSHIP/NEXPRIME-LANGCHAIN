from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide

from app.models.user import User


class UserCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session

    async def get_users(self) -> list[User]:
        query = await self.session.execute(select(User))
        return query.scalars().all()

    async def save(self, user: User) -> User:
        user.create_user_id = user.user_id
        user.modified_user_id = user.user_id
        self.session.add(user)
        return user

    async def get_user(self, user_id: str) -> User | None:
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()
