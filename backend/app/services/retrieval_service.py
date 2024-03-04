from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores.qdrant import Qdrant

from app.cores.config import settings
import app.cores.dependencies as deps
from app.schemas import retreival_schema as schema


class RetrievalService:
    def __init__(self, request: schema.QueryInput) -> None:
        self.request = request
        self.vectorstore: Qdrant = Qdrant.construct_instance(
            texts=[""],
            embedding=deps.get_embedding(request.embedding_model),
            url=settings.vectorstore.url,
            collection_name=request.collection,
        )
        self.llm = ChatOpenAI(
            model=request.llm_model, temperature=0, api_key=settings.OPENAI_API_KEY
        )

    @property
    def prompt_template(self) -> ChatPromptTemplate:
        from langchain import hub

        return hub.pull("langchain-ai/retrieval-qa-chat")

    def retrieve(self) -> dict[str, Any]:
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain

        document_chain = create_stuff_documents_chain(self.llm, self.prompt_template)
        retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response: dict[str, Any] = retrieval_chain.invoke({"input": self.request.query})
        return response
