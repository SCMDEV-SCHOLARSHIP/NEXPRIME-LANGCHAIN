import asyncio
from typing import Callable, Any
from logging import Logger

from dependency_injector.wiring import inject, Provide
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

import app.cores.common_types as types


class TokenMetricsCallbackHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.prompt_tokens + self.completion_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
        )

    @inject
    async def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        token_encoder_factory: Callable[[str], types.TokenEncoder] = Provide[
            "token_encoder_factory.provider"
        ],
        **kwargs: Any,
    ) -> None:
        prompt = prompts[0]
        model_name: str = serialized["kwargs"]["model"]  # TODO: 테스트 필요
        token_encoder = token_encoder_factory(model_name)
        encoded_tokens = token_encoder(prompt)
        self.prompt_tokens += len(encoded_tokens)

    async def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[types.BaseMessage]],
        **kwargs: Any,
    ) -> None:
        tasks = asyncio.gather(
            *[
                self.on_llm_start(
                    serialized,
                    ["\n".join([msg.type.upper(), str(msg.content)])],
                    **kwargs,
                )
                for msg in messages[0]
            ]
        )
        return await tasks

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.completion_tokens += 1

    @inject
    async def on_llm_end(
        self,
        response: LLMResult,
        logger: Logger = Provide["logger"],
        **kwargs: Any,
    ) -> None:
        logger.info(
            (
                f"Tokens Used: {self.prompt_tokens + self.completion_tokens}\n"
                f"\tPrompt Tokens: {self.prompt_tokens}\n"
                f"\tCompletion Tokens: {self.completion_tokens}\n"
            )
        )
