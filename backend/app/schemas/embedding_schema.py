from pydantic import BaseModel


class BaseVectorStoreInfo(BaseModel):
    engine: str
    collection: str


class BaseEmbeddingInfo(BaseModel):
    engine: str
    model: str


class EmbeddingRequest(BaseModel):
    file_path: str
    embedding_model: BaseEmbeddingInfo
    vectorstore: BaseVectorStoreInfo


class DocumentDTO(BaseModel):
    file_path: str
    file_name: str
    ext: str


class EmbeddingPostResponse(BaseModel):
    filepath: str
    split_count: int
    ids: list[int]
    endpoint: int | str
