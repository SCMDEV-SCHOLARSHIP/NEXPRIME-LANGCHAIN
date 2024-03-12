from fastapi import APIRouter, Path, status, Depends
from typing import Callable
from dependency_injector.wiring import inject, Provide

from app.cores.di_container import DiContainer
import app.schemas.collection_schema as schema
from app.services.collection_service import CollectionService

router = APIRouter(prefix="/collections")


@router.get(
    "/{collection}/documents/{doc_id}",
    response_model=schema.RecordResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def get_document_from_id(
    collection: str = Path(),
    doc_id: int = Path(),
    service_factory: Callable[..., CollectionService] = Depends(
        Provide[DiContainer.collection_service_factory.provider]
    ),
):
    service = service_factory(collection_name=collection)
    results = service.get_doc(doc_id)
    return schema.RecordResponse(results=results)


@router.delete(
    "/{collection}/documents/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
def delete_document_from_id(
    collection: str = Path(),
    doc_id: int = Path(),
    service_factory: Callable[..., CollectionService] = Depends(
        Provide[DiContainer.collection_service_factory.provider]
    ),
) -> None:
    # deleted_record_ids = [rec.id for rec in service.search_doc(collection, doc_id)] # 삭제된 포인트 id를 알고 싶을 때
    service = service_factory(collection_name=collection)
    service.delete_doc(doc_id)
    return
