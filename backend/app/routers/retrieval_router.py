from fastapi import APIRouter, status

import app.schemas.retreival_schema as schema
import app.services.retrieval_service as service


router = APIRouter(prefix="/retrieval")


@router.post("/", response_model=schema.QueryOutput, status_code=status.HTTP_200_OK)
def retrieve_by_query(ret_req: schema.QueryInput) -> schema.QueryOutput:
    serv = service.RetrievalService(ret_req)
    result = serv.retrieve()
    response = schema.QueryOutput(
        answer=result["answer"],
        sources=[
            " ".join(
                [doc.metadata["source"], "--SPLIT", str(doc.metadata["split_number"])]
            )
            for doc in result["context"]
        ],
    )
    return response
