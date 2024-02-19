from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter

from ..cores.dependencies import get_loader, get_embedding, get_vectorstore_crud
from ..schemas.embedding_schema import EmbeddingRequest, DocumentMetaSchema
from ..models.document import DocumentMeta


def embed_documents(emb_req: EmbeddingRequest) -> list[DocumentMetaSchema]:
    embedding_model = get_embedding(emb_req.embedding_model)
    vectorstore = get_vectorstore_crud(emb_req.vectorstore)(
        embedding_model=embedding_model,
        info=emb_req.vectorstore,
    )
    results: list[DocumentMetaSchema] = []
    for f in emb_req.files:
        path = Path(f.file_path)
        loader = get_loader(f.file_path)
        loaded_documents = loader.load()
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        splitted_documents = text_splitter.split_documents(loaded_documents)
        total_split = len(splitted_documents)
        metadatas = [
            DocumentMeta(
                **f.model_dump(),
                name=path.name,
                stem=path.stem,
                ext=path.suffix,
                total_split=total_split,
                split_number=i,
            )
            for i in range(1, total_split + 1)
        ]
        uuid_results = vectorstore.create(splitted_documents, metadatas=metadatas)
        vectorstore.info.recreate = False
        results.append(
            DocumentMetaSchema(
                file_path=f.file_path,
                name=path.name,
                total_split=total_split,
                ids=uuid_results,
            )
        )
    return results
    """url = settings.vectorstore.url
    qdrant = Qdrant.from_documents(
        splitted_documents,
        embedding_model,
        url=url,
        collection_name=emb_req.vectorstore.collection,
        force_recreate=True,
    )"""
    """
        qdrant = Qdrant(
        client=QdrantClient("localhost"),
        collection_name="sample_2",
        embeddings=get_embedding(emb_req.embedding_model)
    )"""
