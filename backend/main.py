import uvicorn
from fastapi.responses import RedirectResponse

from app import create_app
from app.cores.config import settings


app = create_app()


@app.get("/")
def show_api_docs():  # 편의 상, 실행 시 바로 api docs로 연결. 나중에 삭제
    return RedirectResponse("http://localhost:8000/docs")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.environ.host, port=settings.environ.port, reload=True
    )
