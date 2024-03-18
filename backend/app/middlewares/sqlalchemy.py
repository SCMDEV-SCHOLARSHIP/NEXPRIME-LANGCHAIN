from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from app.database.rdb.session import set_session_context, reset_session_context, session
from fastapi.logger import logger


class SQLAlchemyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)
        logger.debug(
            f"[SQLAlchemyMiddleware] set session context with session_id : {session_id}"
        )
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            logger.debug("[SQLAlchemyMiddleware] Remove session")
            await session.remove()
            logger.debug("[SQLAlchemyMiddleware] reset session")
            reset_session_context(context=context)
