from __future__ import annotations
from typing import Any, AsyncGenerator, Callable, Hashable
from abc import ABC, abstractmethod

from langchain import hub
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory

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

    async def retrieve(
        self,
        query: str,
        history_func: Callable[..., types.BaseChatMessageHistory],
        **identifiers: Hashable,
    ) -> dict[str, Any]:
        chain = self.create_final_chain(history_func)
        response: dict[str, Any] = await chain.ainvoke(
            {"input": query}, config={"configurable": identifiers}
        )
        return response

    async def stream(
        self,
        query: str,
        history_func: Callable[..., types.BaseChatMessageHistory],
        **identifiers: Hashable,
    ) -> AsyncGenerator[str, None]:
        chain = self.create_final_chain(history_func)
        sources: list[str] = []
        async for chunk in chain.astream(
            {"input": query}, config={"configurable": identifiers}
        ):
            chunk: types.AddableDict
            context: list[types.Document] | None = chunk.get("context", None)
            if context:  # TODO: sources 볼 수 있는 내장 기능 찾아보기
                sources.extend(
                    [
                        " ".join(
                            [
                                doc.metadata["source"],
                                "--SPLIT",
                                str(doc.metadata["split_number"]),
                            ]
                        )
                        for doc in context
                    ]
                )
            answer: str | None = chunk.get("answer", None)
            if answer is not None:
                yield answer
        yield "\n\nSources:\n"
        for src in sources:  # TODO: sources 볼 수 있는 내장 기능 찾아보기
            yield src + "\n"

    @property
    def contextualize_prompt_template(self) -> ChatPromptTemplate:
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, formulate a standalone question "
            "which can be understood without the chat history.\n"
            "Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return contextualize_q_prompt

    def create_final_chain(
        self, history_func: Callable[..., types.BaseChatMessageHistory]
    ) -> types.Runnable:
        retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )
        document_chain = create_stuff_documents_chain(self.llm, self.prompt_template)
        retrieval_chain = create_history_aware_retriever(
            self.llm, retriever, self.contextualize_prompt_template
        )
        rag_chain = create_retrieval_chain(retrieval_chain, document_chain)

        conversational_chain = RunnableWithMessageHistory(
            rag_chain,
            history_func,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        return conversational_chain


class OpenAIRetrievalService(RetrievalService):

    @property
    def prompt_template(self) -> ChatPromptTemplate:  # test template
        return hub.pull("langchain-ai/retrieval-qa-chat")


class BaseRetrievalService(RetrievalService):

    @property
    def prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Answer any use questions based solely on the context below:\n"
                        "<context>\n"
                        "{context}\n"
                        "</context>"
                    ),
                ),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
