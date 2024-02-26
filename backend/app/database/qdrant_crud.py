from langchain.vectorstores.qdrant import Qdrant
from qdrant_client import QdrantClient, models

import app.cores.common_types as types

from .vectorstore_crud import VectorStoreCRUD
from ..cores.config import settings
from ..models.document import DocumentMeta


class QdrantCRUD(VectorStoreCRUD):
    client = QdrantClient(url=settings.vectorstore.url)

    def create(
        self,
        documents: list[types.Document],
        metadatas: list[DocumentMeta] | None = None,
        collection_recreate: bool = False,
    ) -> list[str]:
        texts = [d.page_content for d in documents]
        qdrant: Qdrant = Qdrant.construct_instance(
            texts,
            embedding=self.embedding_model,
            url=settings.vectorstore.url,
            collection_name=self.collection_name,
            force_recreate=collection_recreate,
        )
        return qdrant.add_texts(
            texts,
            metadatas=(
                [m.model_dump() for m in metadatas] if metadatas != None else None
            ),
        )

    def read(self, doc_id: int) -> list[types.Record]:
        results: list[types.Record] = []
        more_page = None
        while True:
            records, more_page = self.__class__.client.scroll(
                self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.file_id",
                            match=models.MatchValue(value=doc_id),
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
        self.__class__.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.file_id",
                            match=models.MatchValue(value=doc_id),
                        ),
                    ],
                )
            ),
        )
        return
