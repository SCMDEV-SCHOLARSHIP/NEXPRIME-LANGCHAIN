from fastapi import FastAPI

from app.cores.config import settings
import app.routers as routers


def create_app() -> FastAPI:
    app = FastAPI(title=settings.environ.project_name)
    app.include_router(router=routers.collection_apis, tags=["Collection"])
    app.include_router(router=routers.embedding_apis, tags=["Embedding"])
    return app
