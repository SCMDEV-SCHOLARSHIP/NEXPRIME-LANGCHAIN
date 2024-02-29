from abc import ABC, abstractmethod
from typing import Any
from langchain_core.documents import Document

import app.cores.common_types as types

from ..models.document import DocumentMeta


class VectorStoreCRUD(ABC):
    client: types.Client = None

    def __init__(
        self, collection_name: str = "", embedding_model: types.Embeddings | None = None
    ) -> None:
        self.collection_name: str = collection_name
        self.embedding_model: types.Embeddings | None = embedding_model

    @abstractmethod
    def create(
        self,
        documents: list[Document],
        metadatas: list[DocumentMeta] | None = None,
        **kwargs: Any
    ) -> list[str]:
        """Create vectors

        Returns:
            list[str]: list of ids in uuid
        """

    @abstractmethod
    def read(self, doc_id: int, **kwargs: Any) -> list[types.Record]: ...

    @abstractmethod
    def delete(self, doc_id: int, **kwargs: Any) -> None: ...
