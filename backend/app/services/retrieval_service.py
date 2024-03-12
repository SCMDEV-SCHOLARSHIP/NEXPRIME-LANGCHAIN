import asyncio
from typing import Any
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

import app.cores.common_types as types


class RetrievalService(ABC):
    def __init__(
        self, vectorstore: types.VectorStore, llm: types.BaseLanguageModel
    ) -> None:
        self.llm = llm
        self.vectorstore = vectorstore

    @property
    @abstractmethod
    def prompt_template(self) -> ChatPromptTemplate: ...

    async def retrieve(self, query: str) -> dict[str, Any]:
        document_chain = create_stuff_documents_chain(self.llm, self.prompt_template)
        retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response: dict[str, Any] = await retrieval_chain.ainvoke({"input": query})
        return response


class OpenAIRetrievalService(RetrievalService):

    @property
    def prompt_template(self) -> ChatPromptTemplate:  # test template
        return hub.pull("langchain-ai/retrieval-qa-chat")
