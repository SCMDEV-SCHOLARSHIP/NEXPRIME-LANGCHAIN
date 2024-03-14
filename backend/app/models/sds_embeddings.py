import requests
from langchain_core.embeddings import Embeddings
import json
from dependency_injector.wiring import inject, Provide

from app.cores.config import ConfigContianer


class SDSEmbedding(Embeddings):
    @inject
    def __init__(
        self, url: str = Provide[ConfigContianer.config.secrets.SDS_EMBEDDING_URL]
    ) -> None:
        self.url = url
        super().__init__()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._get_embeded_vectors(texts)

    def embed_query(self, text: str) -> list[float]:
        pass

    def _get_embeded_vectors(self, texts: list[str]) -> list[list[float]]:
        url = self.url
        headers = {"Content-Type": "application/json"}

        # request body
        data = {"instances": texts}

        try:
            # make request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            vectors = json.loads(response.content.decode("utf-8"))["predictions"]
            return vectors
        except requests.exceptions.RequestException as e:  # Handle exceptions
            # TODO: Need to define Error code
            print("Error: ", e)
            return []
