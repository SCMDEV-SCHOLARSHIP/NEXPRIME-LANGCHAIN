import asyncio
from typing import Coroutine, Any

import app.cores.common_types as types
from app.cores.utils import gen_id
import app.schemas.embedding_schema as schema

# TODO: 추후 기능을 사용하지 않으면 삭제하기
from .collection_service import CollectionService


class EmbeddingService:
    def __init__(self, collection_service: CollectionService) -> None:
        self.vectorstore = collection_service.vectorstore
        self.get_doc = collection_service.get_doc
        self.delete_doc = collection_service.delete_doc

    async def embed_doc(
        self,
        splitted_document: list[types.Document],
        doc_info: schema.DocumentInfo,
        collection_recreate: bool = False,
    ) -> schema.EmbeddingResultSchema:
        total_split = len(splitted_document)
        metadata_coros = [
            schema.create_doc_meta(doc_info, total_split, i)
            for i, _ in enumerate(splitted_document, start=1)
        ]
        metadatas = await asyncio.gather(*metadata_coros)
        uuid_results = await self.vectorstore.aadd_documents(
            splitted_document,
            metadatas=[m.model_dump() for m in metadatas],
            collection_recreate=collection_recreate,
        )
        return await schema.create_emb_result(metadatas[0], uuid_results)

    async def embed_docs(
        self,
        splitted_documents: list[list[types.Document]],
        doc_infos: list[schema.DocumentInfo],
        collection_recreate: bool = False,
    ) -> list[schema.EmbeddingResultSchema]:
        results: list[schema.EmbeddingResultSchema] = []
        docs = iter(splitted_documents)
        if collection_recreate == True:
            infos = iter(doc_infos)
            doc, info = next(docs), next(infos)
            results.append(await self.embed_doc(doc, info, True))
            embed_coros = [self.embed_doc(doc, info) for doc, info in zip(docs, infos)]
        else:
            existences = await asyncio.gather(
                *[self.get_doc(gen_id(info.source)) for info in doc_infos]
            )
            infos = iter(doc_infos)
            embed_coros: list[Coroutine[Any, Any, schema.EmbeddingResultSchema]] = []
            for doc, info, doc_exist in zip(docs, infos, existences):
                if doc_exist:
                    # TODO: logging 또는 langchain 기능으로 변경
                    print(f"\033[33mWARNING: {info.source} has been passed\033[0m")
                    continue
                embed_coros.append(self.embed_doc(doc, info))
        results.extend(await asyncio.gather(*embed_coros))
        return results
