from uuid import uuid4
from logging import Logger
from starlette.types import ASGIApp, Receive, Scope, Send
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from app.database.rdb.session import set_session_context, reset_session_context, session
from app.cores.logger import logger


class SQLAlchemyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    @inject
    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        logger: Logger = Provide["logger"],
    ) -> None:
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)
        logger.debug(
            f"[{self.__class__.__name__}] set session context with session_id : {session_id}"
        )
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            logger.debug(f"[{self.__class__.__name__}] Remove session")
            await session.remove()
            logger.debug(f"[{self.__class__.__name__}] reset session")
            reset_session_context(context=context)
