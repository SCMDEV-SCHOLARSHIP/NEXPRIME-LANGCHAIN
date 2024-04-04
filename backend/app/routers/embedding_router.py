import asyncio
from fastapi import APIRouter, Path, status, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from typing import Callable, Coroutine, Any

import app.cores.common_types as types
from app.cores.utils import HEADERS, gen_id
from app.cores.di_container import DiContainer
from app.services import EmbeddingService
import app.schemas.embedding_schema as schema


router = APIRouter(prefix="/embeddings/documents", dependencies=[HEADERS["AT"]])


@router.post(
    "/",
    response_model=schema.EmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def embed_new_documents(
    emb_req: schema.BatchEmbeddingRequest,
    service_factory: Callable[..., Coroutine[Any, Any, EmbeddingService]] = Depends(
        Provide[DiContainer.embedding_service_factory.provider]
    ),
    splitted_doc_factory: Callable[
        ..., Coroutine[Any, Any, list[types.Document]]
    ] = Depends(Provide[DiContainer.splitted_document_factory.provider]),
) -> schema.EmbeddingResponse:
    service_task = asyncio.create_task(
        service_factory(
            collection_name=emb_req.collection,
            embedding_model_name=emb_req.embedding_model,
        )
    )
    splitted_documents = await asyncio.gather(
        *[splitted_doc_factory(file_path=file.source) for file in emb_req.files]
    )
    service = await service_task
    results = await service.embed_docs(
        splitted_documents, emb_req.files, emb_req.collection_recreate
    )
    return schema.EmbeddingResponse(results=results)


@router.put(
    "/{doc_id}",
    response_model=schema.EmbeddingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@inject
async def re_embed_document(
    emb_req: schema.ReplacementEmbeddingRequest,
    doc_id: int = Path(),
    service_factory: Callable[..., Coroutine[Any, Any, EmbeddingService]] = Depends(
        Provide[DiContainer.embedding_service_factory.provider]
    ),
    splitted_doc_factory: Callable[
        ..., Coroutine[Any, Any, list[types.Document]]
    ] = Depends(Provide[DiContainer.splitted_document_factory.provider]),
) -> schema.EmbeddingResponse:
    if doc_id != gen_id(emb_req.file.source):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "not matched id")
    service, splitted_document = await asyncio.gather(
        service_factory(
            collection_name=emb_req.collection,
            embedding_model_name=emb_req.embedding_model,
        ),
        splitted_doc_factory(file_path=emb_req.file.source),
    )
    try:
        await service.delete_doc(doc_id)
    except:
        # TODO: logging 또는 delete 함수 오버라이딩 쪽으로 넘기기
        print(f"\033[33mWARNING: File id {doc_id} does not exist. Create new...\033[0m")
    return schema.EmbeddingResponse(
        results=[await service.embed_doc(splitted_document, emb_req.file)]
    )
