from pydantic import BaseModel

from app.schemas.message_schema import MessageIdentifierRequest


class RetrievalInput(MessageIdentifierRequest, extra="forbid"):
    query: str
    collection: str
    llm_model: str
    embedding_model: str


class RetrievalOutput(BaseModel, extra="forbid"):
    answer: str
    sources: list[str]
