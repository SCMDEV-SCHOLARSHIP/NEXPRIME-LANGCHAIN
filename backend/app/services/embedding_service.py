from pathlib import Path
from qdrant_client import QdrantClient
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.qdrant import Qdrant
from qdrant_client import models

from ..cores.config import settings
from ..cores.dependencies import get_loader, get_embedding
from ..schemas.embedding_schema import DocumentDTO, EmbeddingRequest


def load_vectorstore(vectorstore: str):
    if vectorstore == "qdrant":
        pass


def embed_document(document: DocumentDTO, emb_req: EmbeddingRequest):
    loader = get_loader(emb_req.file_path)
    loaded_documents = loader.load()
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    splitted_documents = text_splitter.split_documents(loaded_documents)
    embedding_model = get_embedding(emb_req.embedding_model)
    url = settings.vectorstore.url
    qdrant = Qdrant.from_documents(
        splitted_documents,
        embedding_model,
        url=url,
        collection_name=emb_req.vectorstore.collection,
        force_recreate=True,
    )
    """
        qdrant = Qdrant(
        client=QdrantClient("localhost"),
        collection_name="sample_2",
        embeddings=get_embedding(emb_req.embedding_model)
    )"""
