from pydantic import BaseModel, Field

import app.cores.common_types as types


class DocumentInfo(BaseModel, extra="forbid"):
    source: str
    category: str
    subject: str | None = None


class BaseEmbeddingRequest(BaseModel, extra="forbid"):
    model: str
    collection: str


class SingleDocument(BaseEmbeddingRequest, extra="forbid"):
    file: DocumentInfo


class BatchDocuments(BaseEmbeddingRequest, extra="forbid"):
    files: list[DocumentInfo]


class EmbeddingFile(SingleDocument, extra="forbid"):
    collection_recreate: bool = False


class EmbeddingFiles(BatchDocuments, extra="forbid"):
    collection_recreate: bool = False


class DocumentMetaSchema(BaseModel, extra="forbid"):
    file_id: int
    source: str
    file_name: str = Field(alias="name")
    total_split: int
    point_ids: list[str]


class BaseResponse(BaseModel, extra="forbid"): ...


class SingleResult(BaseResponse, extra="forbid"):
    result: BaseModel


class BatchResults(BaseResponse, extra="forbid"):
    results: list[BaseModel]


class EmbeddingResult(SingleResult, extra="forbid"):
    result: DocumentMetaSchema


class EmbeddingResults(BatchResults, extra="forbid"):
    results: list[DocumentMetaSchema]


class RecordResults(BaseResponse, extra="forbid"):
    results: list[types.Record] | None = None
