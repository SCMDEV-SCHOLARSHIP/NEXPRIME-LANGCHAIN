from fastapi import APIRouter, Path, status

import app.cores.dependencies as deps
import app.schemas.embedding_schema as schema
import app.services.collection_service as service

router = APIRouter(prefix="/collections")


@router.get(
    "/{collection}/documents/{doc_id}",
    response_model=schema.RecordResults,
    status_code=status.HTTP_200_OK,
)
def get_document_from_id(collection: str = Path(), doc_id: int = Path()):
    results = service.search_doc(collection, doc_id)
    return schema.RecordResults(results=results)


@router.delete(
    "/{collection}/documents/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_from_id(collection: str = Path(), doc_id: int = Path()) -> None:
    # deleted_record_ids = [rec.id for rec in service.search_doc(collection, doc_id)] # 삭제된 포인트 id를 알고 싶을 때
    service.delete_doc(collection, doc_id)
    return
