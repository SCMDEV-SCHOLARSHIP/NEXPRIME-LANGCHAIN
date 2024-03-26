from sqlalchemy import select
from sqlalchemy.sql import cast
from sqlalchemy.dialects.postgresql import UUID

from app.models.embedding_file import File
from app.database.rdb import session
from typing import Type, Dict, List, Any


class FileCrud:
    @staticmethod
    async def filtering(query: Type[select], filters: Dict[str, List[Any]]) -> callable:
        forbidden_columns = ['delete_yn']
        valid_columns = {column.name: column.type for column in File.__table__.columns}
        
        for column_name, values in filters.items():
            if column_name in forbidden_columns or column_name not in valid_columns.keys():
                del filters[column_name]
            else:
                valid_type = valid_columns[column_name]
                filters[column_name] = [cast(value, valid_type) for value in values]
        
        for column_name, value_list in filters.items():
            query = query.filter(getattr(File, column_name).in_(value_list))
        return query

    async def get_files(self) -> list[File]:
        query = await session.execute(select(File))
        return query.scalars().all()

    async def save(self, file: File) -> File:
        session.add(file)
        return await self.get_file({"uuid": [file.uuid]})

    async def get_file(self, filters: Dict[str, List[Any]], delete_yn: bool|None=None) -> File:
        query = select(File).where(delete_yn or True)
        query = await self.filtering(query, filters)
        result = await session.execute(query)
        return result.scalars().first()