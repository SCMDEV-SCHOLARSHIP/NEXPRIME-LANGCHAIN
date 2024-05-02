from typing import Hashable

from dependency_injector.wiring import inject
from langchain_core.messages import HumanMessage, AIMessage

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.schemas.message_schema import MessageHistoryDTO, convert_message_dto_to_message
from app.repository import MessageHistoryCrud

import app.cores.common_types as types
from app.database.rdb import Transactional, Propagation


class DBMessageService:
    @inject
    def __init__(self, message_crud: MessageHistoryCrud) -> None:
        self.message_crud = message_crud

    @property
    def message_mapping(self) -> dict[str, type[types.BaseMessage]]:
        return {"ai": AIMessage, "human": HumanMessage}

    async def load_messages(self, **filter_kwargs: Hashable) -> list[types.BaseMessage]:
        raw_messages = await self.message_crud.get_messages(**filter_kwargs)
        mapping = self.message_mapping
        messages: list[types.BaseMessage] = [
            mapping[raw_msg.sender](content=raw_msg.content) for raw_msg in raw_messages
        ]
        return messages

    @Transactional(propagation=Propagation.REQUIRED)
    async def save_messages(
        self, messages: list[types.BaseMessage], **identifiers: Hashable
    ) -> None:
        N = len(messages)
        try:
            message_dtos = [
                MessageHistoryDTO(
                    **identifiers,
                    sender=messages[i].type,
                    content=messages[i].content,
                    sources=None,
                )
                for i in range(N - 2, N)
            ]
        except:
            raise InvalidRequestException("identifiers", ErrorCode.INVALID_FORMAT)
        db_messages = [convert_message_dto_to_message(dto) for dto in message_dtos]
        await self.message_crud.save_messages(db_messages)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_messages(self, **filter_kwargs: Hashable) -> None:
        await self.message_crud.delete_messages(**filter_kwargs)
