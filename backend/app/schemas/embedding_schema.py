from pydantic import BaseModel, Field


class BaseFileInfo(BaseModel):
    file_path: str
    category: str
    subject: str | None = None


class BaseVectorStoreInfo(BaseModel):
    engine: str
    collection: str
    recreate: bool = False


class BaseEmbeddingInfo(BaseModel):
    engine: str
    model: str


class EmbeddingRequest(BaseModel):
    files: list[BaseFileInfo]
    embedding_model: BaseEmbeddingInfo
    vectorstore: BaseVectorStoreInfo


class DocumentMetaSchema(BaseModel):
    file_path: str
    file_name: str = Field(alias="name")
    total_split: int
    ids: list[str]


class EmbeddingPostResponse(BaseModel):
    collection: str
    results: list[DocumentMetaSchema]
