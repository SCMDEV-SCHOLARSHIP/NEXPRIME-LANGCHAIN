import asyncio
from typing import Sequence, Any
from langchain.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient, AsyncQdrantClient
import qdrant_client.models as rest
from dependency_injector.wiring import inject, Provide

from app.cores.config import ConfigContianer
import app.cores.common_types as types
from app.models.sds_embeddings import SDSEmbedding


class ExtendedQdrant(Qdrant):
    @inject
    def __init__(
        self,
        collection_name: str,
        embeddings: types.Embeddings | None = None,
        distance_strategy: str = "COSINE",
        vector_name: str | None = None,
        url: str = Provide[ConfigContianer.config.vectorstore.url],
    ):
        client = QdrantClient(url=url)
        async_client = AsyncQdrantClient(url=url)
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

    def add_documents(
        self,
        documents: list[types.Document],
        metadatas: list[dict[str, Any]] | None = None,
        collection_recreate: bool = False,
        ids: Sequence[str] | None = None,
        batch_size: int = 64,
        **kwargs: Any
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
        return super().add_texts(texts, metadatas, ids, batch_size, **kwargs)

    async def aadd_documents(
        self,
        documents: list[types.Document],
        metadatas: list[dict[str, Any]] | None = None,
        collection_recreate: bool = False,
        ids: Sequence[str] | None = None,
        batch_size: int = 64,
        **kwargs: Any
    ) -> list[str]:
        texts = [d.page_content for d in documents]
        if collection_recreate == True:  # Qdrant 내부 동작
            partial_embeddings = await self.embeddings.aembed_documents([""])
            vector_size = len(partial_embeddings[0])
            vectors_config = rest.VectorParams(
                size=vector_size, distance=rest.Distance[self.distance_strategy]
            )
            if self.vector_name is not None:
                vectors_config = {
                    self.vector_name: vectors_config,
                }
            await self.async_client.recreate_collection(
                collection_name=self.collection_name, vectors_config=vectors_config
            )
        return await super().aadd_texts(texts, metadatas, ids, batch_size, **kwargs)

    def get_records(self, doc_id: int) -> list[types.Record]:
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

    async def aget_records(self, doc_id: int) -> list[types.Record]:
        results: list[types.Record] = []
        more_page = None
        while True:
            records, more_page = await self.async_client.scroll(
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
