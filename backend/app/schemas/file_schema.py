from pydantic import BaseModel, Field, validator, UUID4
from app.models.embedding_file import File
from typing import Optional
from datetime import datetime
from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode
from platform import system
# import re     # [SCMDEV-79] kevin delete

class FileDTO(BaseModel, extra="forbid"):
    uuid: UUID4
    file_path: str
    file_name: str
    file_extension: str
    create_datetime: Optional[datetime] = Field(default=None)
    create_user_id: Optional[str] = Field(default=None)
    modified_datetime: Optional[datetime] = Field(default=None)
    modified_user_id: Optional[str] = Field(default=None)

    @validator("file_path")
    def validate_file_path(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("file_path", error_code=ErrorCode.NOT_EXIST)
        
        # [SCMDEV-79] kevin delete {
        # pattern = r'^[a-zA-Z]:\\(?:[\w\s\-_]+\\)*[\w\s\-_]+(?:\.\w+)?$' if system() == "Windows" else r'^\/(?:[\w\d\s_-]+\/)*[\w\d\s_-]+(?:\.\w+)?$'
        # if not re.match(pattern, value):
        #     raise InvalidRequestException(
        #         "file_path",
        #         ErrorCode(
        #             code="KMG_ERR_I_001", message="file_path is not valid format"
        #         ),
        #     )
        # [SCMDEV-79] kevin delete }
        return value
    
    @validator("file_name")
    def validate_file_name(cls, value):
        if not value or len(value) == 0:
            raise InvalidRequestException("file_name", error_code=ErrorCode.NOT_EXIST)
        return value

def convert_file_to_file_dto(file: File|None) -> FileDTO:
    if file is None:
        return file
    file_dict: dict = file.__dict__
    del file_dict["delete_yn"]
    del file_dict["_sa_instance_state"]
    return FileDTO(**file_dict)

def convert_file_dto_to_file(file_dto: FileDTO) -> File:
    file_dict: dict = file_dto.__dict__
    return File(**file_dict)