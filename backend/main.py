import uvicorn
from app.cores.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.environ.host,
        port=settings.environ.port,
        reload=True,
    )
