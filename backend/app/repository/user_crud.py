from sqlalchemy import select

from app.models.user import User
from app.database.rdb import session
from typing import Optional


class UserCrud:
    async def get_users(self) -> list[User]:
        query = await session.execute(select(User))
        return query.scalars().all()

    async def save(self, user: User) -> User:
        user.create_user_id = user.user_id
        user.modified_user_id = user.user_id
        session.add(user)
        return user

    async def get_user(self, user_id: str) -> User:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().first()
