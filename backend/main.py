import os

import uvicorn
from dependency_injector.providers import Configuration

from app import app


if __name__ == "__main__":
    config: Configuration = app.config
    base_config = config.base
    if base_config.langsmith_tracing() == True:
        langsmith_config = config.secrets.langsmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = str(langsmith_config.project())
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = str(langsmith_config.api_key())

    uvicorn.run(
        "app:app",
        host=base_config.host(),
        port=base_config.port(),
        reload=True,
    )
