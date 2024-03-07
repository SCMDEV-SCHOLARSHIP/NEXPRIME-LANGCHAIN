from typing import TypeAlias
from langchain.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseLanguageModel
from langchain.vectorstores import VectorStore
from qdrant_client import QdrantClient
import qdrant_client.http.models as qtypes

Record: TypeAlias = qtypes.Record
Client: TypeAlias = QdrantClient
ExtendedId: TypeAlias = qtypes.ExtendedPointId
