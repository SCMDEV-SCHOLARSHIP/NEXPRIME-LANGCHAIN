from fastapi import APIRouter

from ..schemas.embedding_schema import EmbeddingRequest, EmbeddingPostResponse
from ..services.embedding_service import embed_documents as run_embedding


router = APIRouter(prefix="/embeddings/documents")


@router.post("/", response_model=EmbeddingPostResponse)
def embed_new_documents(emb_req: EmbeddingRequest):
    results = run_embedding(emb_req)
    return EmbeddingPostResponse(
        collection=emb_req.vectorstore.collection,
        results=results,
    )
