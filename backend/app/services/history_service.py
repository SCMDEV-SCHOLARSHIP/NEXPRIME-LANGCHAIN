from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeAlias, Hashable

from dependency_injector.providers import Aggregate
from dependency_injector.wiring import inject, Provide

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

from app.cores.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

import app.cores.common_types as types


_HistoryKeyType: TypeAlias = tuple[Hashable, ...]


class MemoryHistoryService:
    @inject
    def __init__(
        self,
        strategy_aggregate: Aggregate[MemoryStrategy] = Provide[
            "memory_strategy.provider"
        ],
    ) -> None:
        self.chat_histories: dict[_HistoryKeyType, types.BaseChatMessageHistory] = {}
        self.memory_mapping: dict[str, MemoryStrategy] = {
            memory_type: strategy()
            for memory_type, strategy in strategy_aggregate.providers.items()
        }

    def get_strategy(self, memory_type: str) -> MemoryStrategy:
        strategy = self.memory_mapping.get(memory_type, None)
        if strategy is None:
            raise InvalidRequestException("memory_type", ErrorCode.BAD_REQUEST)
        return strategy

    def make_key(self, **key_kwargs: Hashable) -> tuple[Hashable, ...]:
        try:
            return (key_kwargs["user_id"],)
        except:
            raise InvalidRequestException("identifier", ErrorCode.BAD_REQUEST)

    def get_session_history(self, user_id: str) -> types.BaseChatMessageHistory:
        key = self.make_key(user_id=user_id)
        if key not in self.chat_histories:
            self.chat_histories[key] = ChatMessageHistory()
        return self.chat_histories[key]

    async def reconstruct(
        self,
        memory_type: str,
        llm: types.BaseLanguageModel,
        cut_off: int,
        **key_kwargs: Hashable,
    ) -> None:
        memory_strategy = self.get_strategy(memory_type)
        history = self.get_session_history(**key_kwargs)
        await memory_strategy.reconstruct(history, llm=llm, cut_off=cut_off)

    def delete_history(self, **key_kwargs: Hashable) -> None:
        key = self.make_key(**key_kwargs)
        self.chat_histories.pop(key, None)


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


"""
class SummaryBufferMemory(BaseSummaryMemoryStrategy):
    async def reconstruct(
        self,
        history: types.BaseChatMessageHistory,
        max_token_limit: int = 512,
        **kwargs,
    ) -> None:
        messages = history.messages
        # TODO: 토큰 수를 넘길 때만 요약하도록 변경
"""
