from typing import List
import requests
from langchain_core.embeddings import Embeddings
import json

class SDSEmbedding(Embeddings):

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeded_vectors(texts)

    def embed_query(self, text: str) -> List[float]:
        pass

    def _get_embeded_vectors(self, texts: List[str]) -> List[List[float]]:
        url = "http://sds-embed.serving.70-220-152-1.sslip.io/v1/models/embed:predict"
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