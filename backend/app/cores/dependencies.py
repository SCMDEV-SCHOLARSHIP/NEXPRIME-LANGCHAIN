import asyncio
from pathlib import Path
from abc import ABC
from typing import TypeAlias, TypeVar
from dependency_injector.wiring import inject

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

from langchain_openai import ChatOpenAI

from app.database import ExtendedQdrant

import app.cores.common_types as types
from app.cores.config import settings
from app.cores.constants import SupportedModels, SupportedVectorStores

from app.services import (
    RetrievalService,
    OpenAIRetrievalService,
    EmbeddingService,
    CollectionService,
)


class FeatureBuilder(ABC):
    async def make_vectorstore(
        self, collection_name: str, embedding_model: types.Embeddings
    ) -> types.VectorStore:
        vs_name = settings.vectorstore.engine
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
                openai_api_key=settings.OPENAI_API_KEY,
            )
        elif engine == "sds-embed":
            return SDSEmbedding()
        else:
            raise Exception("Value not found")


class DocumentBuilder(FeatureBuilder):
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


class RetrievalBuilder(FeatureBuilder):
    async def make_llm(self, model_name: str) -> types.BaseLanguageModel:
        engine = SupportedModels.LLM.get(model_name, None)
        if engine == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            raise Exception("Value not found")


# TODO: TypeVar 테스트
# BuilderType: TypeAlias = DocumentBuilder | RetrievalBuilder # TypeVar 문제 발생 시 변경
BuilderType = TypeVar("BuilderType", DocumentBuilder, RetrievalBuilder)


class FeatureDirector:
    async def check_valid_builder(
        self, builder: BuilderType, builder_type: type[BuilderType]
    ) -> None:
        if isinstance(builder, builder_type) == False:
            raise Exception(f"{type(builder)} is not allowed")

    @inject
    async def build_retrieval_service(
        self,
        builder: BuilderType,
        collection_name: str,
        embedding_model_name: str,
        llm_model_name: str,
        alias: str = "openai-test",
    ) -> RetrievalService:
        await self.check_valid_builder(builder, RetrievalBuilder)
        embedding = await builder.make_embedding(embedding_model_name)
        vectorstore, llm = await asyncio.gather(
            builder.make_vectorstore(collection_name, embedding),
            builder.make_llm(llm_model_name),
        )
        if alias == "openai-test":
            return OpenAIRetrievalService(vectorstore=vectorstore, llm=llm)
        else:
            raise Exception("Value not found")

    @inject
    async def build_embedding_service(
        self,
        builder: BuilderType,
        collection_name: str,
        embedding_model_name: str,
    ) -> EmbeddingService:
        embedding = await builder.make_embedding(embedding_model_name)
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return EmbeddingService(CollectionService(vectorstore))

    @inject
    async def build_collection_service(
        self, builder: BuilderType, collection_name: str
    ) -> CollectionService:
        embedding = SDSEmbedding()
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return CollectionService(vectorstore)

    @inject
    async def build_splitted_documents(
        self, builder: BuilderType, file_path: str, splitter_alias: str = "base"
    ) -> list[types.Document]:
        await self.check_valid_builder(builder, DocumentBuilder)
        loader, text_splitter = await asyncio.gather(
            builder.make_loader(file_path), builder.make_splitter(splitter_alias)
        )
        loaded_documents = loader.load()
        splitted_documents = text_splitter.split_documents(loaded_documents)
        return splitted_documents
