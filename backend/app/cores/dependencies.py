from pathlib import Path

from langchain_community.document_loaders.base import BaseLoader
from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.pdf import PyPDFLoader

from langchain_core.embeddings import Embeddings
from langchain.embeddings.openai import OpenAIEmbeddings

from ..schemas.embedding_schema import BaseEmbeddingInfo, BaseVectorStoreInfo
from ..cores.config import settings
from ..database import CRUD
from ..database.qdrant_crud import QdrantCRUD
from ..models.SDSEmbeddings import SDSEmbedding


def get_loader(file_path: str) -> BaseLoader:
    ext = Path(file_path).suffix
    if ext == ".txt":
        return TextLoader(file_path)
    elif ext == ".doc" or ext == "docx":
        return Docx2txtLoader(file_path)
    elif ext == ".pdf":
        return PyPDFLoader(file_path)
    else:
        raise Exception("document loader error")


def get_embedding(info: BaseEmbeddingInfo) -> Embeddings:
    if info.engine == "openai":
        return OpenAIEmbeddings(
            model=info.model,
            openai_api_key=settings.environ.OPENAI_API_KEY,
        )
    elif info.engine == "sds-embed":
        return SDSEmbedding()
    else:
        raise Exception("embedding model error")


def get_vectorstore_crud(info: BaseVectorStoreInfo) -> type[CRUD]:
    if info.engine == "qdrant":
        return QdrantCRUD
    else:
        raise Exception("vectorstore error")
