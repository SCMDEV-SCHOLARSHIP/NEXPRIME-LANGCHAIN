import app.cores.dependencies as deps
import app.cores.common_types as types


def search_doc(collection_name: str, doc_id: int) -> list[types.Record]:
    vectorstore = deps.get_vectorstore_crud()(collection_name=collection_name)
    results = vectorstore.read(doc_id)
    results.sort(
        key=lambda rec: rec.payload["metadata"]["split_number"]
    )  # just sorting
    return results


def delete_doc(collection_name: str, doc_id: int) -> None:
    vectorstore = deps.get_vectorstore_crud()(collection_name=collection_name)
    return vectorstore.delete(doc_id)
