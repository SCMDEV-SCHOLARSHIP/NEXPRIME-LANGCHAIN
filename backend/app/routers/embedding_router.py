from fastapi import APIRouter, Path, status, HTTPException

import app.services.embedding_service as service
import app.schemas.embedding_schema as schema

from ..cores.utils import gen_id


router = APIRouter(prefix="/embeddings/documents")


@router.post(
    "/",
    response_model=schema.EmbeddingResults,
    status_code=status.HTTP_201_CREATED,
)
def embed_new_documents(emb_req: schema.EmbeddingFiles) -> schema.EmbeddingResults:
    return schema.EmbeddingResults(results=service.embed_docs(emb_req))


@router.put(
    "/{doc_id}",
    response_model=schema.EmbeddingResult,
    status_code=status.HTTP_202_ACCEPTED,
)
def re_embed_document(
    emb_req: schema.SingleDocument, doc_id: int = Path()
) -> schema.EmbeddingResult:
    if doc_id != gen_id(emb_req.file.source):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "not matched id")

    from app.services.collection_service import delete_doc

    delete_doc(emb_req.collection, doc_id)
    return schema.EmbeddingResult(result=service.embed_doc(emb_req))
