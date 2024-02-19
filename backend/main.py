import uvicorn
from fastapi import FastAPI

from app.cores.config import settings
from app.routers.embedding_router import router as embedding_router


app = FastAPI(title=settings.environ.project_name)
app.include_router(router=embedding_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
