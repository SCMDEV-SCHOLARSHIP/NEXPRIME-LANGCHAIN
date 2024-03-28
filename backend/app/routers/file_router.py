from fastapi import APIRouter, status, Depends, File, UploadFile
from pydantic import UUID4
from app.schemas.file_schema import FileDTO
from dependency_injector.wiring import inject, Provide
from app.cores.di_container import DiContainer
from app.services.file_service import FileService
from typing import Dict, List

router = APIRouter(prefix="/files")


@router.post(
    "/{user_id}",
    response_model=FileDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Upload New File",
)
@inject
async def create_file(
    file: UploadFile = File(...),
    user_id: str = "admin",     # TODO Session에서 현재 접속 중인 user_id를 받도록 처리되어야 함
    file_service: FileService = Depends(Provide[DiContainer.file_service]),
) -> FileDTO:

    ret_file = await file_service.create_file(file, user_id)
    return ret_file

@router.get(
    "/",
    response_model=list[FileDTO],
    status_code=status.HTTP_200_OK,
    summary="Get All Files",
)
@inject
async def get_files(
    file_service: FileService = Depends(Provide[DiContainer.file_service]),
) -> list[FileDTO]:
    
    ret_files = await file_service.get_files()
    return ret_files

## TODO : Filter 조건으로 조회하는 API 구현
# @router.get(
#     "/{filters}",
#     response_model=FileDTO,
#     status_code=status.HTTP_200_OK,
#     summary="Get file with filter: Dict[str, List[str]]",
# )
# @inject
# async def get_file(
#     filters: Dict[str, List[str]],
#     file_service: FileService = Depends(Provide[DiContainer.file_service]),
# ) -> list[FileDTO]:
    
#     ret_file = await file_service.get_file(filters)
#     return ret_file