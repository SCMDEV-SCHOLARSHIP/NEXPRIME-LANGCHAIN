from fastapi import FastAPI
from pathlib import Path
from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.document_loaders.text import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.azure_openai import AzureOpenAIEmbeddings
from typing import TypeAlias
from langchain.vectorstores import VectorStore
from langchain.vectorstores.qdrant import Qdrant

from ..schemas.embedding_schema import BaseEmbeddingInfo, BaseVectorStoreInfo
from ..cores.config import settings


LoderType: TypeAlias = Docx2txtLoader | TextLoader
EmbeddingType: TypeAlias = OpenAIEmbeddings | AzureOpenAIEmbeddings


def get_loader(file_path: str) -> LoderType:
    ext = Path(file_path).suffix
    if ext == ".txt":
        return TextLoader(file_path)
    elif ext == ".doc" or "docx":
        return Docx2txtLoader(file_path)
    else:
        raise Exception("document loader error")


def get_embedding(info: BaseEmbeddingInfo) -> EmbeddingType:
    if info.engine == "openai":
        return OpenAIEmbeddings(
            model=info.model,
            openai_api_key=settings.environ.OPENAI_API_KEY,
        )
    else:
        raise Exception("embedding model error")


def get_vectorstore(info: BaseVectorStoreInfo) -> VectorStore:
    if info.engine == "qdrant":
        return
