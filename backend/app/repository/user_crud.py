from sqlalchemy import select

from app.models.user import User
from app.database.rdb import session


class UserCrud:
    async def get_users(self) -> list[User]:
        query = await session.execute(select(User))
        return query.scalars().all()

    async def save(self, user: User) -> User:
        user.create_user_id = user.user_id
        user.modified_user_id = user.user_id
        session.add(user)
        return user
