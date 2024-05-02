from typing import Literal, Any
from datetime import datetime

from pydantic import BaseModel, Field

import app.cores.common_types as types
from app.models.chat_message import MessageHistory


class MessageIdentifierRequest(BaseModel, extra="forbid"):
    pass


# TODO: langchain이 pydantic v2 지원하면 삭제, BaseMessage로 교체
class MessageResponse(BaseModel, extra="allow"):
    content: str
    type: str
    additional_kwargs: dict = Field(default_factory=dict)


def parse_messages_to_response(
    messages: list[types.BaseMessage],
) -> list[MessageResponse]:
    return [MessageResponse(**msg.__dict__) for msg in messages]


class MessageHistoryDTO(BaseModel, extra="forbid"):
    user_id: str
    sender: Literal["ai", "human"]
    content: str
    sources: list[str] | None = None
    create_datetime: datetime | None = None
    create_user_id: str | None = None
    modified_datetime: datetime | None = None
    modified_user_id: str | None = None


def convert_message_to_message_dto(
    message: MessageHistory | None,
) -> MessageHistoryDTO | None:
    if message is None:
        return message
    message_dict: dict = message.__dict__
    del message_dict["message_id"]
    del message_dict["delete_yn"]
    del message_dict["_sa_instance_state"]
    return MessageHistoryDTO(**message_dict)


def convert_message_dto_to_message(message_dto: MessageHistoryDTO) -> MessageHistory:
    file_dict: dict = message_dto.__dict__
    return MessageHistory(**file_dict)


def extract_identifiers(keywords: dict[str, Any]) -> dict[str, Any]:
    return {
        k: v for k, v in keywords.items() if k in MessageIdentifierRequest.model_fields
    }
