from datetime import datetime
from typing import TypeVar

from sqlalchemy import select, update, Select, Update
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.models.chat_message import MessageHistory

_QT = TypeVar("_QT", Select, Update)


class MessageHistoryCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session

    async def get_messages(self, **filter_kwargs) -> list[MessageHistory]:
        query = select(MessageHistory).order_by(MessageHistory.create_datetime.asc())
        filter_kwargs.update({"delete_yn": False})
        query = self.filtering(query, **filter_kwargs)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def save_messages(self, messages: list[MessageHistory]) -> None:
        self.session.add_all(messages)
        return

    async def delete_messages(self, **filter_kwargs) -> None:
        query = update(MessageHistory)
        query = self.filtering(query, **filter_kwargs)
        query = query.values(
            delete_yn=True,
            modified_datetime=datetime.now(),
            modified_user_id=filter_kwargs.get("user_id", None)
            or MessageHistory.user_id,
        )
        await self.session.execute(query)

    def filtering(self, query: _QT, **filter_kwargs) -> _QT:
        for attr, value in filter_kwargs.items():
            try:
                query = query.filter(getattr(MessageHistory, attr) == value)
            except:
                raise InvalidRequestException(attr, ErrorCode.NOT_EXIST)
        return query
