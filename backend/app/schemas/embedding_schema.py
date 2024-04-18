from pathlib import Path
from pydantic import BaseModel

from app.cores.utils import gen_id


class DocumentInfo(BaseModel, extra="forbid"):
    source: str
    category: str
    subject: str | None = None


class DocumentMeta(BaseModel, extra="forbid"):
    file_id: int
    source: str
    category: str
    subject: str | None = None
    name: str
    stem: str
    ext: str
    total_split: int
    split_number: int


class EmbeddingResultSchema(BaseModel, extra="forbid"):
    file_id: int
    source: str
    name: str
    total_split: int
    point_ids: list[str]


async def create_doc_meta(
    doc_info: DocumentInfo, total_split: int, split_number: int
) -> DocumentMeta:
    path = Path(doc_info.source)
    return DocumentMeta(
        **doc_info.model_dump(),
        file_id=gen_id(doc_info.source),
        name=path.name,
        stem=path.stem,
        ext=path.suffix,
        total_split=total_split,
        split_number=split_number,
    )


async def create_emb_result(
    doc_meta: DocumentMeta, uuids: list[str]
) -> EmbeddingResultSchema:
    return EmbeddingResultSchema(
        file_id=doc_meta.file_id,
        source=doc_meta.source,
        name=doc_meta.name,
        total_split=doc_meta.total_split,
        point_ids=uuids,
    )


class ReplacementEmbeddingRequest(BaseModel, extra="forbid"):
    embedding_model: str
    collection: str
    file: DocumentInfo


class BatchEmbeddingRequest(BaseModel, extra="forbid"):
    embedding_model: str
    collection: str
    files: list[DocumentInfo]
    collection_recreate: bool = False
    chunk_size: int
    chunk_overlap: int

class EmbeddingResponse(BaseModel, extra="forbid"):
    results: list[EmbeddingResultSchema]
