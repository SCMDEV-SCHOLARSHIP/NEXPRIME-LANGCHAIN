from fastapi import APIRouter, status, Depends
from dependency_injector.wiring import inject, Provide

from app.cores.utils import HEADERS
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
    llm_service: LlmService = Depends(Provide[DiContainer.llm_service]),
) -> list[LlmDTO]:
    
    ret_llms = await llm_service.get_llms()
    return ret_llms

@router.post(
    "/register-llm",
    response_model=LlmDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register LLM Model",
)
@inject
async def create_llm_model(
    llm_dto: LlmDTO,
    llm_service: LlmService = Depends(Provide[DiContainer.llm_service]),
) -> LlmDTO:
    
    ret_llm = await llm_service.create_llm(llm_dto)
    return ret_llm
