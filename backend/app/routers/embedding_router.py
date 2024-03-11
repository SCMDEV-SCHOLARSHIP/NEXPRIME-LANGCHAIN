from fastapi import APIRouter, Path, status, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from typing import Callable

from app.cores.di_container import DiContainer
from app.services import EmbeddingService
import app.schemas.embedding_schema as schema
import app.cores.common_types as types


from ..cores.utils import gen_id


router = APIRouter(prefix="/embeddings/documents")


@router.post(
    "/",
    response_model=schema.EmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
def embed_new_documents(
    emb_req: schema.BatchEmbeddingRequest,
    service_factory: Callable[..., EmbeddingService] = Depends(
        Provide[DiContainer.embedding_service_factory.provider]
    ),
    splitted_docs_factory: Callable[..., list[types.Document]] = Depends(
        Provide[DiContainer.splitted_documents_factory.provider]
    ),
) -> schema.EmbeddingResponse:
    service = service_factory(
        collection_name=emb_req.collection, embedding_model_name=emb_req.embedding_model
    )
    splitted_documents = [
        splitted_docs_factory(file_path=file.source) for file in emb_req.files
    ]
    results = service.embed_docs(
        splitted_documents, emb_req.files, emb_req.collection_recreate
    )
    return schema.EmbeddingResponse(results=results)


@router.put(
    "/{doc_id}",
    response_model=schema.EmbeddingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@inject
def re_embed_document(
    emb_req: schema.ReplacementEmbeddingRequest,
    doc_id: int = Path(),
    embedding_service_factory: Callable[..., EmbeddingService] = Depends(
        Provide[DiContainer.embedding_service_factory.provider]
    ),
    splitted_docs_factory: Callable[..., list[types.Document]] = Depends(
        Provide[DiContainer.splitted_documents_factory.provider]
    ),
) -> schema.EmbeddingResponse:
    if doc_id != gen_id(emb_req.file.source):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "not matched id")
    service = embedding_service_factory(
        collection_name=emb_req.collection, embedding_model_name=emb_req.embedding_model
    )
    splitted_document = splitted_docs_factory(file_path=emb_req.file.source)
    try:
        service.delete_doc(doc_id)
    except:
        # TODO: logging 또는 delete 함수 오버라이딩 쪽으로 넘기기
        print(f"\033[33mWARNING: File id {doc_id} does not exist. Create new...\033[0m")
    return schema.EmbeddingResponse(
        results=[service.embed_doc(splitted_document, emb_req.file)]
    )
