from typing import TypeAlias
from langchain.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
import qdrant_client.http.models as qtypes

Record: TypeAlias = qtypes.Record
Client: TypeAlias = QdrantClient
ExtendedId: TypeAlias = qtypes.ExtendedPointId
