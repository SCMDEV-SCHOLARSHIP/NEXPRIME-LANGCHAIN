from fastapi import APIRouter, status, Depends
from dependency_injector.wiring import inject, Provide

import app.schemas.retreival_schema as schema
from app.cores.di_container import DiContainer, RetrievalServiceBuilder


router = APIRouter(prefix="/retrieval")


@router.post("/", response_model=schema.RetrievalOutput, status_code=status.HTTP_200_OK)
@inject
def retrieve_by_query(
    ret_req: schema.RetrievalInput,
    service_builder: RetrievalServiceBuilder = Depends(Provide[DiContainer.retrieval_service_builder]),
) -> schema.RetrievalOutput:
    service = service_builder.build_retrieval_service(
        llm_model_name=ret_req.llm_model,
        embedding_model_name=ret_req.embedding_model,
        vectorstore_params={"collection_name": ret_req.collection},
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
