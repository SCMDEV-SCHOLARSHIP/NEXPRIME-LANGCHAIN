from pydantic import BaseModel

from app.schemas import embedding_schema as emb_schema


class RetrievalInput(emb_schema.BaseEmbeddingRequest, extra="forbid"):
    query: str
    llm_model: str


class RetrievalOutput(BaseModel, extra="forbid"):
    answer: str
    sources: list[str]
