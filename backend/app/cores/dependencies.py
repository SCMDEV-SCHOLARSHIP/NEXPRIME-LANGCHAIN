from pathlib import Path

from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.html import UnstructuredHTMLLoader
from langchain.embeddings.openai import OpenAIEmbeddings

import app.cores.common_types as types

from ..cores.config import settings
from ..cores.constants import SupportedModels, SupportedVectorStores
from ..database import VectorStoreCRUD, QdrantCRUD


def get_loader(file_path: str) -> types.BaseLoader:
    ext = Path(file_path).suffix
    if ext == ".txt":
        return TextLoader(file_path)
    elif ext == ".docx":
        return Docx2txtLoader(file_path)
    elif ext == ".html":
        return UnstructuredHTMLLoader(file_path)
    else:
        raise Exception("document loader error")


def get_embedding(model_name: str) -> types.Embeddings:
    engine = SupportedModels.EMBEDDING.get(model_name, None)
    if engine == "openai":
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    else:
        raise Exception("embedding model error")


def get_vectorstore_crud() -> type[VectorStoreCRUD]:
    vs_name = settings.vectorstore.engine
    if vs_name == SupportedVectorStores.QDRANT:
        return QdrantCRUD
    else:
        raise Exception("vectorstore error")
