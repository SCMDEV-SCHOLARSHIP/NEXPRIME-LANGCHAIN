from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import app.routers as routers
from app.middlewares import SQLAlchemyMiddleware, JWTAuthMiddleware

from app.cores.exceptions import EXC_HDLRs
from app.cores.di_container import DiContainer

# from app.cores.config import ConfigContianer


def create_app() -> FastAPI:
    di_container = DiContainer()
    # config_container = ConfigContianer()

    di_container.wire(packages=["app"])
    # config_container.wire(packages=["app"])

    app = FastAPI(
        title=di_container.config.base.project_name(),
        exception_handlers=EXC_HDLRs if EXC_HDLRs else None,
    )

    app.container = di_container
    app.config = di_container.config

    app.include_router(router=routers.collection_apis, tags=["Collection"])
    app.include_router(router=routers.embedding_apis, tags=["Embedding"])
    app.include_router(router=routers.retrieval_apis, tags=["Retrieval"])
    app.include_router(router=routers.user_apis, tags=["User"])
    app.include_router(router=routers.file_apis, tags=["File"])
    app.include_router(router=routers.auth_apis, tags=["Authentication(Token)"])
    app.include_router(router=routers.login_apis, tags=["Login/Logout"])

    token_validator = di_container.auth_service().get_strategy("default").validate

    app.add_middleware(JWTAuthMiddleware, token_validator=token_validator)
    app.add_middleware(SQLAlchemyMiddleware)

    return app


app = create_app()


@app.get("/")
def show_api_docs():  # 편의 상, 실행 시 바로 api docs로 연결. 나중에 삭제
    return RedirectResponse("http://localhost:8000/docs")
