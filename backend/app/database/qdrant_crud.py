from langchain.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient, AsyncQdrantClient
import qdrant_client.models as rest

import app.cores.common_types as types

from ..cores.config import settings
from ..models.document import DocumentMeta
from app.models.sds_embeddings import SDSEmbedding


class ExtendedQdrant(Qdrant):
    def __init__(
        self,
        collection_name: str,
        embeddings: types.Embeddings | None = None,
        distance_strategy: str = "COSINE",
        vector_name: str | None = None,
        async_client: AsyncQdrantClient | None = None,
    ):
        client = QdrantClient(url=settings.vectorstore.url)
        if embeddings == None:  # TODO: 예외처리 또는 구조 변경
            embeddings = SDSEmbedding()
        super().__init__(
            client=client,
            collection_name=collection_name,
            embeddings=embeddings,
            distance_strategy=distance_strategy,
            vector_name=vector_name,
            async_client=async_client,
        )

    def create(
        self,
        documents: list[types.Document],
        metadatas: list[DocumentMeta] | None = None,
        collection_recreate: bool = False,
    ) -> list[str]:
        texts = [d.page_content for d in documents]
        if collection_recreate == True:  # Qdrant 내부 동작
            partial_embeddings = self.embeddings.embed_documents([""])
            vector_size = len(partial_embeddings[0])
            vectors_config = rest.VectorParams(
                size=vector_size, distance=rest.Distance[self.distance_strategy]
            )
            if self.vector_name is not None:
                vectors_config = {
                    self.vector_name: vectors_config,
                }
            self.client.recreate_collection(
                collection_name=self.collection_name, vectors_config=vectors_config
            )
        return self.add_texts(
            texts,
            metadatas=(
                [m.model_dump() for m in metadatas] if metadatas != None else None
            ),
        )

    def read(self, doc_id: int) -> list[types.Record]:
        results: list[types.Record] = []
        more_page = None
        while True:
            records, more_page = self.client.scroll(
                self.collection_name,
                scroll_filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="metadata.file_id",
                            match=rest.MatchValue(value=doc_id),
                        ),
                    ]
                ),
                offset=more_page,
            )
            results.extend(records)
            if more_page == None:
                break
        return results

    def delete(self, doc_id: int) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(
                filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="metadata.file_id",
                            match=rest.MatchValue(value=doc_id),
                        ),
                    ],
                )
            ),
        )
        return
