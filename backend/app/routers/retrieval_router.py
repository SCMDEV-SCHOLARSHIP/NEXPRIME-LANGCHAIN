from fastapi import APIRouter, status, Depends
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import inject, Provide
from typing import Callable, Coroutine, Any

from app.cores.utils import HEADERS, get_payload_info
import app.schemas.retrieval_schema as schema
from app.cores.di_container import DiContainer
from app.services import RetrievalService


router = APIRouter(prefix="/retrieval", dependencies=[HEADERS["AT"]])


@router.post("/", response_model=schema.RetrievalOutput, status_code=status.HTTP_200_OK)
@inject
async def retrieve_by_query(
    ret_req: schema.RetrievalInput,
    service_factory: Callable[..., Coroutine[Any, Any, RetrievalService]] = Depends(
        Provide[DiContainer.retrieval_service_factory.provider]
    ),
) -> schema.RetrievalOutput:
    service = await service_factory(
        collection_name=ret_req.collection,
        embedding_model_name=ret_req.embedding_model,
        llm_model_name=ret_req.llm_model,
    )
    result = await service.retrieve(ret_req.query)
    response = schema.RetrievalOutput(
        answer=result["answer"],
        sources=[
            " ".join(
                [doc.metadata["source"], "--SPLIT", str(doc.metadata["split_number"])]
            )
            for doc in result["context"]
        ],
    )
    return response


@router.post(
    "/chat-stream", response_class=StreamingResponse, status_code=status.HTTP_200_OK
)
@inject
async def retrieve_streaming_by_query(
    ret_req: schema.RetrievalInput,
    request: Request,
    service_factory: Callable[..., Coroutine[Any, Any, RetrievalService]] = Depends(
        Provide[DiContainer.retrieval_service_factory.provider]
    ),
) -> StreamingResponse:
    service = await service_factory(
        collection_name=ret_req.collection,
        embedding_model_name=ret_req.embedding_model,
        llm_model_name=ret_req.llm_model,
    )
    user_id: str = get_payload_info(request, "sub")
    return StreamingResponse(
        service.stream(ret_req.query, user_id),
        media_type="text/event-stream",
    )
