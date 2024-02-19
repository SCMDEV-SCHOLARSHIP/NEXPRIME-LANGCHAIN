from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain.vectorstores.qdrant import Qdrant

from . import CRUD
from ..cores.config import settings
from ..models.document import DocumentMeta
from ..schemas.embedding_schema import BaseVectorStoreInfo


class QdrantCRUD(CRUD):
    def __init__(
        self,
        embedding_model: Embeddings,
        info: BaseVectorStoreInfo,
    ) -> None:
        self.embedding_model = embedding_model
        self.info = info

    def create(
        self,
        documents: list[Document],
        metadatas: list[DocumentMeta] | None = None,
    ) -> list[str]:
        texts = [d.page_content for d in documents]
        qdrant: Qdrant = Qdrant.construct_instance(
            texts,
            self.embedding_model,
            url=settings.vectorstore.url,
            collection_name=self.info.collection,
            force_recreate=self.info.recreate,
        )
        return qdrant.add_texts(
            texts,
            metadatas=(
                [m.model_dump() for m in metadatas] if metadatas != None else None
            ),
        )
