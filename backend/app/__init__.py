from typing import Generator
from fastapi import FastAPI

from app.cores.config import settings
import app.routers as routers
from app.cores.exceptions import EXC_HDLRs
from app.cores.di import init_di
from app.middlewares import SQLAlchemyMiddleware
from fastapi.responses import RedirectResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.environ.project_name,
        exception_handlers=EXC_HDLRs if EXC_HDLRs else None,
    )
    app.include_router(router=routers.collection_apis, tags=["Collection"])
    app.include_router(router=routers.embedding_apis, tags=["Embedding"])
    app.include_router(router=routers.retrieval_apis, tags=["Retrieval"])
    app.include_router(router=routers.user_apis, tags=["User"])

    app.add_middleware(SQLAlchemyMiddleware)

    init_di()

    return app


app = create_app()


@app.get("/")
def show_api_docs():  # 편의 상, 실행 시 바로 api docs로 연결. 나중에 삭제
    return RedirectResponse("http://localhost:8000/docs")
