from fastapi import APIRouter, status, Depends
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import inject, Provide
from typing import Callable, Coroutine, Any

from app.cores.utils import HEADERS, get_payload_info
import app.schemas.retrieval_schema as schema
from app.schemas.message_schema import extract_identifiers
from app.cores.di_container import DiContainer
from app.services import RetrievalService, MemoryHistoryService


router = APIRouter(prefix="/retrieval", dependencies=[HEADERS["AT"]])


@router.post("/", response_model=schema.RetrievalOutput, status_code=status.HTTP_200_OK)
@inject
async def retrieve_by_query(
    ret_req: schema.RetrievalInput,
    request: Request,
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
    retrieval_service_factory: Callable[
        ..., Coroutine[Any, Any, RetrievalService]
    ] = Depends(Provide[DiContainer.retrieval_service_factory.provider]),
) -> schema.RetrievalOutput:
    service = await retrieval_service_factory(
        collection_name=ret_req.collection,
        embedding_model_name=ret_req.embedding_model,
        llm_model_name=ret_req.llm_model,
    )
    user_id: str = get_payload_info(request, "sub")
    identifiers = extract_identifiers(ret_req.__dict__)

    result = await service.retrieve(
        ret_req.query,
        history_service.get_session_history,
        user_id=user_id,
        **identifiers
    )

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
    history_service: MemoryHistoryService = Depends(
        Provide[DiContainer.history_service]
    ),
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
    identifiers = extract_identifiers(ret_req.__dict__)

    return StreamingResponse(
        service.stream(
            ret_req.query,
            history_service.get_session_history,
            user_id=user_id,
            **identifiers
        ),
        media_type="text/event-stream",
    )
