import asyncio
from typing import Any, AsyncGenerator
from abc import ABC, abstractmethod

from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableBranch, ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory

import app.cores.common_types as types


chat_histories: dict[str, types.BaseChatMessageHistory] = {}


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

    async def stream(self, query: str, user_id: str) -> AsyncGenerator[str, None]:
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

        # history 볼 때 사용
        # TODO: API 만들기
        """
        yield "\nHistories:\n"
        for msg in self.get_session_history(user_id).messages:
            yield str(msg) + "\n"
        """

    def get_session_history(self, user_id: str) -> types.BaseChatMessageHistory:
        if user_id not in chat_histories:
            chat_histories[user_id] = ChatMessageHistory()
        return chat_histories[user_id]

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
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        rag_chain = (
            {
                "input": self.create_reformulate_question_chain(
                    self.llm, self.contextualize_prompt_template
                )
            }
        ) | retrieval_chain

        conversational_chain = RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
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

    # create_history_aware_retriever 내장함수 복사
    def create_reformulate_question_chain(
        self, llm: types.BaseLanguageModel, prompt: types.BasePromptTemplate
    ) -> types.Runnable:
        if "input" not in prompt.input_variables:
            raise ValueError(
                "Expected `input` to be a prompt variable, "
                f"but got {prompt.input_variables}"
            )

        question_chain = RunnableBranch(
            (
                # Both empty string and empty list evaluate to False
                lambda x: not x.get("chat_history", False),
                # If no chat history, then we just pass input
                (lambda x: x["input"]),
            ),
            # If chat history, then we pass inputs to LLM chain
            prompt | llm | StrOutputParser(),
        ).with_config(run_name="chat_chain")
        return question_chain


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
                    """Answer any use questions based solely on the context below:
                    <context>
                    {context}
                    </context>

                    PLACEHOLDER
                    chat_history
                 """,
                ),
                ("human", """{input}"""),
            ]
        )
