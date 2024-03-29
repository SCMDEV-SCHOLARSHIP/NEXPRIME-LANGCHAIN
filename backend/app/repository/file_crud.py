from sqlalchemy import select, Select
from sqlalchemy.sql import cast
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import async_scoped_session
from typing import Any, Callable
from dependency_injector.wiring import inject, Provide

from app.models.embedding_file import File


class FileCrud:
    @inject
    def __init__(self, session: async_scoped_session = Provide["session"]) -> None:
        self.session = session

    @staticmethod
    async def filtering(query: Select, filters: dict[str, list[Any]]) -> Callable:
        forbidden_columns = ["delete_yn"]
        valid_columns = {column.name: column.type for column in File.__table__.columns}

        for column_name, values in filters.items():
            if (
                column_name in forbidden_columns
                or column_name not in valid_columns.keys()
            ):
                del filters[column_name]
            else:
                valid_type = valid_columns[column_name]
                filters[column_name] = [cast(value, valid_type) for value in values]

        for column_name, value_list in filters.items():
            query = query.filter(getattr(File, column_name).in_(value_list))
        return query

    async def get_files(self) -> list[File]:
        query = await self.session.execute(select(File))
        return query.scalars().all()

    async def save(self, file: File) -> File:
        self.session.add(file)
        return await self.get_file({"uuid": [file.uuid]})

    async def get_file(
        self, filters: dict[str, list[Any]], delete_yn: bool | None = None
    ) -> File:
        query = select(File).where(delete_yn or True)
        query = await self.filtering(query, filters)
        result = await self.session.execute(query)
        return result.scalars().first()
