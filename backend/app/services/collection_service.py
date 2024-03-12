import app.cores.common_types as types


class CollectionService:
    def __init__(self, vectorstore: types.VectorStore) -> None:
        self.vectorstore = vectorstore

    async def get_doc(self, doc_id: int) -> list[types.Record]:
        results = await self.vectorstore.aget_records(doc_id)  # ExtendedQdrant에만 있음
        results.sort(
            key=lambda rec: rec.payload["metadata"]["split_number"]
        )  # just sorting
        return results

    async def delete_doc(self, doc_id: int) -> None:
        point_ids = [rec.id for rec in await self.get_doc(doc_id)]
        await self.vectorstore.adelete(point_ids)
        return
