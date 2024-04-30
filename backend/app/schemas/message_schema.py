from typing import Any

from pydantic import BaseModel, Field

import app.cores.common_types as types


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


def extract_identifiers(keywords: dict[str, Any]) -> dict[str, Any]:
    return {
        k: v for k, v in keywords.items() if k in MessageIdentifierRequest.model_fields
    }
