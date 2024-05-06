from fastapi import APIRouter, status, Depends
from dependency_injector.wiring import inject, Provide

from app.cores.utils import HEADERS
from app.cores.di_container import DiContainer
from app.schemas.llm_schema import LlmDTO
from app.services import LlmService

router = APIRouter(prefix="/LLM", dependencies=[HEADERS["AT"]])

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