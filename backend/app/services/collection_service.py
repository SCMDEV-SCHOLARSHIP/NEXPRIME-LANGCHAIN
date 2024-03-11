import app.cores.common_types as types


class CollectionService:
    def __init__(self, vectorstore: types.VectorStore) -> None:
        self.vectorstore = vectorstore

    def get_doc(self, doc_id: int) -> list[types.Record]:
        results = self.vectorstore.get_records(doc_id)
        results.sort(
            key=lambda rec: rec.payload["metadata"]["split_number"]
        )  # just sorting
        return results

    def delete_doc(self, doc_id: int) -> None:
        point_ids = [rec.id for rec in self.get_doc(doc_id)]
        self.vectorstore.delete(point_ids)
        return
