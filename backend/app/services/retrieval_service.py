from __future__ import annotations
import asyncio
from typing import Any, AsyncGenerator
from abc import ABC, abstractmethod

from dependency_injector.providers import Aggregate
from dependency_injector.wiring import inject, Provide

from langchain import hub
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.chat_message_histories import ChatMessageHistory

from app.cores.exceptions import InternalServerException
from app.cores.exceptions.error_code import ErrorCode

import app.cores.common_types as types


chat_histories: dict[str, types.BaseChatMessageHistory] = {}


def get_session_history(user_id: str) -> types.BaseChatMessageHistory:
    if user_id not in chat_histories:
        chat_histories[user_id] = ChatMessageHistory()
    return chat_histories[user_id]


class RetrievalService(ABC):
    @inject
    def __init__(
        self,
        vectorstore: types.VectorStore,
        llm: types.BaseLanguageModel,
        strategy_aggregate: Aggregate[MemoryStrategy] = Provide[
            "memory_strategy.provider"
        ],
    ) -> None:
        self.llm = llm
        self.vectorstore = vectorstore
        self.memory_mapping: dict[str, MemoryStrategy] = {
            login_type: strategy()
            for login_type, strategy in strategy_aggregate.providers.items()
        }

    def get_strategy(self, memory_type: str) -> MemoryStrategy:
        strategy = self.memory_mapping.get(memory_type, None)
        if strategy is None:  # 코딩 에러
            raise InternalServerException(
                "memory_type", ErrorCode.INTERNAL_SERVER_ERROR
            )
        return strategy

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

    async def stream(
        self, query: str, user_id: str, memory_type: str
    ) -> AsyncGenerator[str, None]:
        chain = self.create_final_chain()

        sources: list[str] = []
        async for chunk in chain.astream(
            {"input": query}, config={"configurable": {"user_id": user_id}}
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

        memory_strategy = self.get_strategy(memory_type)
        history = get_session_history(user_id)
        await memory_strategy.reconstruct(history, llm=self.llm, cut_off=6)

        # history 볼 때 사용
        # TODO: API 만들기
        """
        yield "\nHistories:\n"
        for msg in self.get_session_history(user_id).messages:
            yield str(msg) + "\n"
        """

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

    def create_final_chain(self) -> types.Runnable:
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
            get_session_history,
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


class MemoryStrategy(ABC):
    @abstractmethod
    async def reconstruct(
        self, history: types.BaseChatMessageHistory, **kwargs
    ) -> None: ...


class BaseSummaryMemoryStrategy(MemoryStrategy, ABC):
    @property
    def summarization_prompt(self) -> types.BasePromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    (
                        "Distill the above chat messages into a single summary message. "
                        "Include as many specific details as you can."
                    ),
                ),
            ]
        )


class NoMemoryStrategy(MemoryStrategy):
    async def reconstruct(
        self, history: types.BaseChatMessageHistory, *args, **kwargs
    ) -> None:
        await history.aclear()
        return


class BufferMemoryStrategy(MemoryStrategy):
    async def reconstruct(
        self, history: types.BaseChatMessageHistory, **kwargs
    ) -> None:
        # 기본은 buffer 동작
        return


class BufferWindowMemoryStrategy(MemoryStrategy):
    async def reconstruct(
        self, history: types.BaseChatMessageHistory, cut_off: int = 6, **kwargs
    ) -> None:
        messages = history.messages
        if len(messages) <= cut_off:
            return
        start_idx = len(messages) - cut_off
        trimmed_messages = messages[start_idx:]
        await history.aclear()
        await history.aadd_messages(trimmed_messages)
        return


class SummaryMemoryStrategy(BaseSummaryMemoryStrategy):
    async def reconstruct(
        self,
        history: types.BaseChatMessageHistory,
        llm: types.BaseLanguageModel,
        **kwargs,
    ) -> None:
        messages = history.messages
        if len(messages) == 0:
            return

        summarization_chain = self.summarization_prompt | llm
        summary_message = await summarization_chain.ainvoke({"chat_history": messages})
        await history.aclear()
        await history.aadd_messages([summary_message])
        return


class SummaryBufferMemory(BaseSummaryMemoryStrategy):
    async def reconstruct(
        self,
        history: types.BaseChatMessageHistory,
        max_token_limit: int = 512,
        **kwargs,
    ) -> None:
        messages = history.messages
        # TODO: 토큰 수를 넘길 때만 요약하도록 변경
