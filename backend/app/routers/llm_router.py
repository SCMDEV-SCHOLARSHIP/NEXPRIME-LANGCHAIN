from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide

from app.cores.utils import HEADERS, get_payload_info
from app.cores.di_container import DiContainer
from app.schemas.llm_schema import LlmDTO
from app.services import LlmService

router = APIRouter(prefix="/llm", dependencies=[HEADERS["AT"]])

@router.get(
    "/", 
    response_model=list[LlmDTO],
    status_code=status.HTTP_200_OK,
    summary="Get All LLM models",
)
@inject
async def get_llm_models(
    request: Request,
    llm_service: LlmService = Depends(Provide[DiContainer.llm_service]),
) -> list[LlmDTO]:
    
    user_id: str = get_payload_info(request, "sub")
    ret_llms = await llm_service.get_llms(user_id)
    return ret_llms

@router.post(
    "/register-llm",
    response_model=LlmDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register LLM Model",
)
@inject
async def create_llm_model(
    request: Request,
    llm_dto: LlmDTO,
    llm_service: LlmService = Depends(Provide[DiContainer.llm_service]),
) -> LlmDTO:
    
    user_id: str = get_payload_info(request, "sub")
    ret_llm = await llm_service.create_llm(user_id, llm_dto)
    return ret_llm

@router.delete(
    "/delete-llm",
    response_model=LlmDTO,
    status_code=status.HTTP_200_OK,
    summary="Delete LLM model",
)
@inject
async def delete_llm_model(
    request: Request,
    llm_type: str,
    llm_name: str,
    llm_service: LlmService = Depends(Provide[DiContainer.llm_service]),
) -> LlmDTO:
    
    user_id: str = get_payload_info(request, "sub")
    deleted_llm = await llm_service.delete_llm(user_id, llm_name, llm_type)
    return deleted_llm