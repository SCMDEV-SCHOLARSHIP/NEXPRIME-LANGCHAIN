from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide

from app.cores.utils import HEADERS, get_payload_info
from app.cores.di_container import DiContainer, RetrievalBuilder

import app.schemas.history_schema as schema
import app.schemas.message_schema as msg_schema
from app.schemas.llm_schema import LlmDTO
from app.services import LlmService
from app.services.history_service import MemoryHistoryService


router = APIRouter(prefix="/history", dependencies=[HEADERS["AT"]])


@router.get(
    "", response_model=list[msg_schema.MessageResponse], status_code=status.HTTP_200_OK
)
@inject
async def get_history(
    request: Request,
    identifiers_query: msg_schema.MessageIdentifierRequest = Depends(),
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
) -> list[msg_schema.MessageResponse]:
    user_id: str = get_payload_info(request, "sub")
    identifiers = msg_schema.extract_identifiers(identifiers_query.__dict__)
    history = history_service.get_session_history(user_id=user_id, **identifiers)
    return msg_schema.parse_messages_to_response(history.messages)


@router.post("/reconstruction", status_code=status.HTTP_202_ACCEPTED)
@inject
async def reconstruct_history(
    memory_req: schema.ReconstructionRequest,
    request: Request,
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
    llm_builder: RetrievalBuilder = Depends(Provide[DiContainer.retrieval_builder]),
    llm_service: LlmService = Depends(
        Provide[DiContainer.llm_service]
    )
) -> None:
    user_id: str = get_payload_info(request, "sub")
    memory_type = memory_req.memory_type
    if memory_req.llm_model == "open-ai":
        llm_dto = LlmDTO()
        llm_dto.llm_type = "open-ai"
    else:
        llm_dto = await llm_service.get_llm(user_id, memory_req.llm_model)
    llm = await llm_builder.make_llm(llm_dto)
    identifiers = msg_schema.extract_identifiers(memory_req.__dict__)
    await history_service.reconstruct(
        memory_type, llm, memory_req.cut_off, user_id=user_id, **identifiers
    )
    return


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_history(
    request: Request,
    identifiers_query: msg_schema.MessageIdentifierRequest = Depends(),
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
) -> None:
    user_id: str = get_payload_info(request, "sub")
    identifiers = msg_schema.extract_identifiers(identifiers_query.__dict__)
    history_service.delete_history(user_id=user_id, **identifiers)
    return
