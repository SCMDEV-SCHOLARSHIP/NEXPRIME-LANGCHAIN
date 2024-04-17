from typing import TypeAlias

from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import VectorStore

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables.utils import AddableDict
from langchain_core.chat_history import BaseChatMessageHistory

from qdrant_client import QdrantClient
import qdrant_client.http.models as qtypes

Record: TypeAlias = qtypes.Record
Client: TypeAlias = QdrantClient
ExtendedId: TypeAlias = qtypes.ExtendedPointId
