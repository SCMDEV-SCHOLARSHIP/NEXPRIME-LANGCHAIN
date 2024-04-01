from contextvars import ContextVar, Token
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
    AsyncEngine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Union
from dependency_injector.wiring import inject, Provider
from dependency_injector.providers import Configuration


Base = declarative_base()


class AsyncSessionManager:
    def __init__(self) -> None:
        self.db_url = self.make_db_url()
        self.session_context: ContextVar[str] = ContextVar("session_context")
        self.engine = self.create_async_engine()
        self.async_session_factory = sessionmaker(bind=self.engine, class_=AsyncSession)
        self.session = async_scoped_session(
            session_factory=self.async_session_factory,
            scopefunc=self.get_session_id,
        )

    @inject
    def make_db_url(self, db_config: Configuration = Provider["config.db"]) -> str:
        return (
            "postgresql+asyncpg"
            f"://{db_config.username()}"
            f":{db_config.password()}"
            f"@{db_config.url()}"
        )

    def get_session_id(self) -> str:
        return self.session_context.get()

    def set_session_context(self, session_id: str) -> Token:
        return self.session_context.set(session_id)

    def reset_session_context(self, context: Token) -> None:
        self.session_context.reset(context)

    @inject
    def create_async_engine(
        self, db_config: Configuration = Provider["config.db"]
    ) -> AsyncEngine:
        return create_async_engine(
            self.db_url,
            pool_recycle=3600,
            pool_size=10,
            echo=db_config.sql_log(),
        )
