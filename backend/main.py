import uvicorn
from app import app


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=app.config.base.host(),
        port=app.config.base.port(),
        reload=True,
    )
