import requests
from langchain_core.embeddings import Embeddings
import json
from dependency_injector.wiring import inject, Provide

from app.cores.config import ConfigContianer
from app.cores.exceptions.exceptions import ExternalServiceException
from app.cores.exceptions.error_code import ErrorCode
from app.cores.logger import logger


class SDSEmbedding(Embeddings):
    @inject
    def __init__(
        self, url: str = Provide[ConfigContianer.config.secrets.SDS_EMBEDDING_URL]
    ) -> None:
        self.url = url.get_secret_value()
        super().__init__()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._get_embeded_vectors(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._get_embeded_vectors([text])[0]

    def _get_embeded_vectors(self, texts: list[str]) -> list[list[float]]:
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
