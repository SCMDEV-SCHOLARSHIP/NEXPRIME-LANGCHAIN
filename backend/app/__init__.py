from typing import Generator
from fastapi import FastAPI

from app.cores.config import settings
import app.routers as routers
from app.cores.exceptions import EXC_HDLRs


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.environ.project_name,
        exception_handlers=EXC_HDLRs if EXC_HDLRs else None,
    )
    app.include_router(router=routers.collection_apis, tags=["Collection"])
    app.include_router(router=routers.embedding_apis, tags=["Embedding"])
    app.include_router(router=routers.retrieval_apis, tags=["Retrieval"])
    app.include_router(router=routers.user_apis, tags=["User"])
    return app
