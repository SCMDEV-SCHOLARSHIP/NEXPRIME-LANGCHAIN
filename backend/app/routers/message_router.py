from fastapi import APIRouter, status, Depends, Request
from dependency_injector.wiring import inject, Provide

from app.cores.utils import HEADERS, get_payload_info
from app.cores.di_container import DiContainer

import app.schemas.message_schema as schema
from app.services.message_service import DBMessageService
from app.services.history_service import MemoryHistoryService


router = APIRouter(prefix="/messages", dependencies=[HEADERS["AT"]])


@router.get(
    "", response_model=list[schema.MessageResponse], status_code=status.HTTP_200_OK
)
@inject
async def get_chat_messages(
    request: Request,
    identifiers_query: schema.MessageIdentifierRequest = Depends(),
    message_service: DBMessageService = Depends(Provide[DiContainer.message_service]),
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
) -> list[schema.MessageResponse]:
    user_id: str = get_payload_info(request, "sub")
    identifiers = schema.extract_identifiers(identifiers_query.__dict__)

    messages = await message_service.load_messages(user_id=user_id, **identifiers)
    history = history_service.get_session_history(user_id=user_id, **identifiers)
    if not history.messages:
        await history.aadd_messages(messages)
    return schema.parse_messages_to_response(messages)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@inject
async def save_chat_messages(
    identifiers_req: schema.MessageIdentifierRequest,
    request: Request,
    message_service: DBMessageService = Depends(Provide[DiContainer.message_service]),
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
) -> None:
    user_id: str = get_payload_info(request, "sub")
    identifiers = schema.extract_identifiers(identifiers_req.__dict__)

    history = history_service.get_session_history(user_id=user_id, **identifiers)
    await message_service.save_messages(
        history.messages, user_id=user_id, **identifiers
    )
    return


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_chat_messages(
    request: Request,
    identifiers_query: schema.MessageIdentifierRequest = Depends(),
    message_service: DBMessageService = Depends(Provide[DiContainer.message_service]),
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
) -> None:
    user_id: str = get_payload_info(request, "sub")
    identifiers = schema.extract_identifiers(identifiers_query.__dict__)

    await message_service.delete_messages(user_id=user_id, **identifiers)
    history_service.delete_history(user_id=user_id, **identifiers)
    return
