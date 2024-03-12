from pydantic import BaseModel


class RetrievalInput(BaseModel, extra="forbid"):
    query: str
    collection: str
    llm_model: str
    embedding_model: str


class RetrievalOutput(BaseModel, extra="forbid"):
    answer: str
    sources: list[str]
