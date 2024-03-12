from fastapi import APIRouter, status, Depends
from dependency_injector.wiring import inject, Provide
from typing import Callable

import app.schemas.retreival_schema as schema
from app.cores.di_container import DiContainer
from app.services import RetrievalService


router = APIRouter(prefix="/retrieval")


@router.post("/", response_model=schema.RetrievalOutput, status_code=status.HTTP_200_OK)
@inject
def retrieve_by_query(
    ret_req: schema.RetrievalInput,
    service_factory: Callable[..., RetrievalService] = Depends(
        Provide[DiContainer.retrieval_service_factory.provider]
    ),
) -> schema.RetrievalOutput:
    service = service_factory(
        collection_name=ret_req.collection,
        embedding_model_name=ret_req.embedding_model,
        llm_model_name=ret_req.llm_model,
    )
    result = service.retrieve(ret_req.query)
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
