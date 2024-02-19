from fastapi import APIRouter
from pathlib import Path

from ..schemas.embedding_schema import EmbeddingRequest, DocumentDTO
from ..services.embedding_service import embed_document as run_embedding


router = APIRouter(prefix="/embeddings/document")


@router.post("/")
def embed_new_document(emb_req: EmbeddingRequest):
    file_path = emb_req.file_path
    fpath = Path(file_path)
    document = DocumentDTO(
        file_path=file_path,
        file_name=fpath.name,
        ext=fpath.suffix,
    )
    run_embedding(document, emb_req)
    return "hi"


"""
@router.put("/")
def modify_document(
    file: None,
    model=None,
    vector_db=None,
):  # 임베딩 바디 데이터 받아서 처리
    # vs에 저장된 id를 찾아서 삭제하고 재생성
    # 모델을 수정하거나, vdb를 수정하거나 등등
    result = None  # 처리 함수 호출
    return result  # 결과 직렬화
"""
