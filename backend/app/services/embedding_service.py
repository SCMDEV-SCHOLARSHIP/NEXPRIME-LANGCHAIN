from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter

import app.cores.dependencies as deps
import app.schemas.embedding_schema as schema


from ..cores.utils import gen_id
from ..models.document import DocumentMeta


def embed_doc(emb_req: schema.EmbeddingFile) -> schema.DocumentMetaSchema:
    embedding_model = deps.get_embedding(emb_req.embedding_model)
    vectorstore = deps.get_vectorstore_crud()(
        collection_name=emb_req.collection, embedding_model=embedding_model
    )
    collection_recreate = emb_req.collection_recreate
    file = emb_req.file
    path = Path(file.source)
    loader = deps.get_loader(file.source)
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
            **file.model_dump(),
            file_id=gen_id(file.source),
            name=path.name,
            stem=path.stem,
            ext=path.suffix,
            total_split=total_split,
            split_number=i,
        )
        for i in range(1, total_split + 1)
    ]
    uuid_results = vectorstore.create(
        splitted_documents,
        metadatas=metadatas,
        collection_recreate=collection_recreate,
    )
    return schema.DocumentMetaSchema(
        file_id=metadatas[0].file_id,
        source=file.source,
        name=path.name,
        total_split=total_split,
        point_ids=uuid_results,
    )


def embed_docs(emb_req: schema.EmbeddingFiles) -> list[schema.DocumentMetaSchema]:
    collection_recreate = emb_req.collection_recreate
    results: list[schema.DocumentMetaSchema] = []
    from app.services.collection_service import search_doc

    for f in emb_req.files:
        if collection_recreate == False and search_doc(
            emb_req.collection, gen_id(f.source)
        ):
            print("file already exist")  # logging으로 넘기거나, 다른 로직 추가 가능
            continue
        single_req = schema.EmbeddingFile(
            file=f,
            embedding_model=emb_req.embedding_model,
            collection=emb_req.collection,
            collection_recreate=collection_recreate,
        )
        meta = embed_doc(single_req)
        collection_recreate = False
        results.append(meta)
    return results
