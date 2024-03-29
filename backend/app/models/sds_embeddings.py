import requests
from logging import Logger
from langchain_core.embeddings import Embeddings
import json
from dependency_injector.wiring import inject, Provide

from app.cores.exceptions.exceptions import ExternalServiceException
from app.cores.exceptions.error_code import ErrorCode


class SDSEmbedding(Embeddings):
    @inject
    def __init__(self, url: str = Provide["config.secrets.sds.embedding_url"]) -> None:
        self.url = url
        super().__init__()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._get_embeded_vectors(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._get_embeded_vectors([text])[0]

    @inject
    def _get_embeded_vectors(
        self, texts: list[str], logger: Logger = Provide["logger"]
    ) -> list[list[float]]:
        url = self.url
        headers = {"Content-Type": "application/json"}

        # request body
        data = {"instances": texts}

        logger.info(f"[{self.__class__.__name__}] Get embeded vectors")
        logger.info(f"[{self.__class__.__name__}] url: {url}")
        try:
            # make request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            vectors = json.loads(response.content.decode("utf-8"))["predictions"]
            return vectors
        except requests.exceptions.RequestException as e:  # Handle exceptions
            logger.error(e)
            raise ExternalServiceException(
                "SDS Embedding Model", error_code=ErrorCode.EXTERNAL_SERVICE_ERROR
            )
