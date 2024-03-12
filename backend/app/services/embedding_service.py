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

    def embed_doc(
        self,
        splitted_document: list[types.Document],
        doc_info: schema.DocumentInfo,
        collection_recreate: bool = False,
    ) -> schema.EmbeddingResultSchema:
        total_split = len(splitted_document)
        metadatas = [
            schema.create_doc_meta(doc_info, total_split, i)
            for i, _ in enumerate(splitted_document, start=1)
        ]
        uuid_results = self.vectorstore.add_documents(
            splitted_document,
            metadatas=[m.model_dump() for m in metadatas],
            collection_recreate=collection_recreate,
        )
        return schema.create_emb_result(metadatas[0], uuid_results)

    def embed_docs(
        self,
        splitted_documents: list[list[types.Document]],
        doc_infos: list[schema.DocumentInfo],
        collection_recreate: bool = False,
    ) -> list[schema.EmbeddingResultSchema]:
        recreate = collection_recreate
        results: list[schema.EmbeddingResultSchema] = []
        for doc, info in zip(splitted_documents, doc_infos):
            if recreate == False and self.get_doc(gen_id(info.source)):
                # TODO: logging 또는 langchain 기능으로 변경
                print(f"\033[33mWARNING: {info.source} has been passed\033[0m")
                continue
            res = self.embed_doc(doc, info, recreate)
            results.append(res)
            recreate = False
        return results
