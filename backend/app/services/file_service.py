from asyncio import create_task
import aiofiles
from fastapi import UploadFile
from app.schemas.file_schema import (
    FileDTO,
    convert_file_to_file_dto,
    convert_file_dto_to_file,
)
from dependency_injector.wiring import inject, Provide
from app.repository import FileCrud, UserCrud
from app.database.rdb import Transactional, Propagation
from app.cores.config import ConfigContianer
from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode
from typing import IO, Dict, List, Any
from os.path import join, splitext
from uuid import uuid4


class FileUploadService:

    @inject
    def __init__(
        self,
        file_crud: FileCrud,
        user_crud: UserCrud,
        file_archive_path = Provide[ConfigContianer.config.file_archive.path],
    ) -> None:
        self.file_crud = file_crud
        self.user_crud = user_crud
        self.file_archive_path = file_archive_path
    
    async def generate_uuid(self):
        uuid = uuid4()

        if await self.get_file({"uuid": [uuid]}) is not None:
            uuid = await self.generate_uuid()

        return uuid

    @staticmethod
    async def save_file(save_path: str, file: IO):
        async with aiofiles.open(save_path, "wb") as saved_file:
            await saved_file.write(file.read())
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def create_file(self, file: UploadFile, user_id: str) -> FileDTO:     # TODO : user_id는 임시로 받는 것으로, 추후 session에서 끌고오도록 변경 필요

        if await self.user_crud.get_user(user_id) is None:      # [TODO] Session에서 가져올 user_id가 실존하는지를 검증하는 것이 의미가 있는지 모르겠어서 논의 필요
            raise InvalidRequestException(f"user_id")
        
        task_generate_uuid = create_task(self.generate_uuid())
        file_name, file_extension = splitext(file.filename)
        uuid = await task_generate_uuid
        file_path = join(self.file_archive_path, str(uuid))

        task_save_file = create_task(self.save_file(file_path, file.file))
        
        file_dto = FileDTO(
            uuid=uuid,
            file_path=file_path,
            file_name=file_name,
            file_extension=file_extension,
            create_user_id=user_id,
            modified_user_id=user_id
        )        
        embedding_file = convert_file_dto_to_file(file_dto)
        embedding_file = await self.file_crud.save(file=embedding_file)

        ret_dto = convert_file_to_file_dto(embedding_file)
        await task_save_file
        return ret_dto
    
    async def get_files(self) -> list[FileDTO]:
        files = await self.file_crud.get_files()
        return [convert_file_to_file_dto(file) for file in files]
    
    async def get_file(self, filters: Dict[str, List[Any]]|None) -> FileDTO:
        file = await self.file_crud.get_file(filters)
        return convert_file_to_file_dto(file)