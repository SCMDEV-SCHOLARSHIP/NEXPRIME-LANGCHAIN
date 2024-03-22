import asyncio
from pathlib import Path
from abc import ABC
from typing import TypeAlias, TypeVar, Any
from dependency_injector.wiring import inject, Provide, Provider
from dependency_injector.providers import Configuration

from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.document_loaders.text import TextLoader
from langchain.document_loaders.html import UnstructuredHTMLLoader
from langchain.document_loaders.pdf import PyPDFLoader

from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from langchain.embeddings.openai import OpenAIEmbeddings
from app.models.sds_embeddings import SDSEmbedding
from langchain_community.llms.huggingface_text_gen_inference import (
    HuggingFaceTextGenInference,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain_openai import ChatOpenAI

from app.database import ExtendedQdrant

from app.cores.config import ConfigContianer
import app.cores.common_types as types
from app.cores.constants import SupportedModels, SupportedVectorStores

from app.services import (
    RetrievalService,
    OpenAIRetrievalService,
    BaseRetrievalService,
    EmbeddingService,
    CollectionService,
)


class FeatureBuilder(ABC): ...


class VectorstoreBuilder(FeatureBuilder):
    @inject
    def __init__(
        self, config: Configuration = Provider[ConfigContianer.config]
    ) -> None:
        self.config = config
        super().__init__()

    async def make_vectorstore(
        self, collection_name: str, embedding_model: types.Embeddings
    ) -> types.VectorStore:
        vs_name: str = self.config.vectorstore.engine()
        if vs_name == SupportedVectorStores.QDRANT:
            return ExtendedQdrant(
                collection_name=collection_name, embeddings=embedding_model
            )
        else:
            raise Exception("Value not found")

    async def make_embedding(self, model_name: str) -> types.Embeddings:
        engine = SupportedModels.EMBEDDING.get(model_name, None)
        if engine == "openai":
            return OpenAIEmbeddings(
                model=model_name,
                openai_api_key=self.config.secrets.OPENAI_API_KEY().get_secret_value(),
            )
        elif engine == "sds":
            return SDSEmbedding()
        else:
            raise Exception("Value not found")


class DocumentBuilder(VectorstoreBuilder):
    async def make_loader(self, file_path: str) -> types.BaseLoader:
        ext = Path(file_path).suffix
        if ext == ".txt":
            return TextLoader(file_path)
        elif ext == ".docx":
            return Docx2txtLoader(file_path)
        elif ext == ".html":
            return UnstructuredHTMLLoader(file_path)
        elif ext == ".pdf":
            return PyPDFLoader(file_path)
        else:
            raise Exception("Value not found")

    async def make_splitter(self, alias: str = "base") -> types.TextSplitter:
        if alias == "base":
            return RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", " ", ""],  # default
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,  # default
                is_separator_regex=False,  # defalult
            )
        elif alias == "char":
            return CharacterTextSplitter(
                separator="\n\n",
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False,
            )
        else:
            raise Exception("Value not found")


class RetrievalBuilder(VectorstoreBuilder):
    async def make_llm(self, model_name: str) -> types.BaseLanguageModel:
        engine = SupportedModels.LLM.get(model_name, None)
        if engine == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=self.config.secrets.OPENAI_API_KEY().get_secret_value(),
            )
        elif engine == "sds":
            return HuggingFaceTextGenInference(
                inference_server_url=self.config.secrets.SDS_LLAMA_URL().get_secret_value(),
                max_new_tokens=512,
                top_k=10,
                top_p=0.95,
                typical_p=0.95,
                temperature=0.01,
                repetition_penalty=1.03,
            )
        else:
            raise Exception("Value not found")


# TODO: TypeVar 테스트
# BuilderType: TypeAlias = DocumentBuilder | RetrievalBuilder # TypeVar 문제 발생 시 변경
BuilderType = TypeVar("BuilderType", DocumentBuilder, RetrievalBuilder)


class FeatureDirector(ABC): ...


class ServiceDirector(FeatureDirector):
    @inject
    async def build_retrieval_service(
        self,
        collection_name: str,
        embedding_model_name: str,
        llm_model_name: str,
        alias: str = "base",
        builder: BuilderType = Provide["_retrieval_builder"],
    ) -> RetrievalService:
        embedding = await builder.make_embedding(embedding_model_name)
        vectorstore, llm = await asyncio.gather(
            builder.make_vectorstore(collection_name, embedding),
            builder.make_llm(llm_model_name),
        )
        if alias == "openai-test":
            return OpenAIRetrievalService(vectorstore=vectorstore, llm=llm)
        elif alias == "base":
            return BaseRetrievalService(vectorstore=vectorstore, llm=llm)
        else:
            raise Exception("Value not found")

    @inject
    async def build_embedding_service(
        self,
        collection_name: str,
        embedding_model_name: str,
        builder: BuilderType = Provide["_vectorstore_builder"],
    ) -> EmbeddingService:
        embedding = await builder.make_embedding(embedding_model_name)
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return EmbeddingService(CollectionService(vectorstore))

    @inject
    async def build_collection_service(
        self,
        collection_name: str,
        builder: BuilderType = Provide["_vectorstore_builder"],
    ) -> CollectionService:
        embedding = SDSEmbedding()
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return CollectionService(vectorstore)


class DocumentDirector(FeatureDirector):
    @inject
    async def build_splitted_document(
        self,
        file_path: str,
        splitter_alias: str = "base",
        builder: BuilderType = Provide["_document_builder"],
    ) -> list[types.Document]:
        loader, text_splitter = await asyncio.gather(
            builder.make_loader(file_path), builder.make_splitter(splitter_alias)
        )
        loaded_documents = loader.load()
        splitted_document = text_splitter.split_documents(loaded_documents)
        return splitted_document
