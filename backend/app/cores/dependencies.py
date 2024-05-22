import asyncio
from pathlib import Path
from abc import ABC

from dependency_injector.wiring import inject, Provide, Provider
from dependency_injector.providers import Configuration
import tiktoken
from transformers import AutoTokenizer

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

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from app.models.callbacks import TokenMetricsCallbackHandler

from langchain_openai import ChatOpenAI
from langchain_community.llms.huggingface_text_gen_inference import (
    HuggingFaceTextGenInference,
)

from app.database import ExtendedQdrant

from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

import app.cores.common_types as types
from app.cores.constants import SupportedModels, SupportedVectorStores
from app.cores.exceptions.exceptions import InvalidRequestException
from app.cores.exceptions.error_code import ErrorCode

from app.services import (
    RetrievalService,
    OpenAIRetrievalService,
    BaseRetrievalService,
    EmbeddingService,
    CollectionService,
    LlmService,
)

from app.schemas.llm_schema import LlmDTO


class FeatureBuilder(ABC):
    @inject
    def __init__(self, config: Configuration = Provider["config"]) -> None:
        self.config = config


class VectorstoreBuilder(FeatureBuilder):
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
                openai_api_key=self.config.secrets.openai_api_key(),
            )
        elif engine == "sds":
            return SDSEmbedding()
        else:
            raise Exception("Value not found")


class DocumentBuilder(FeatureBuilder):
    async def make_loader(
        self, file_path: str, extension: str | None = None
    ) -> types.BaseLoader:
        ext = extension
        if ext is None:
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

    async def make_splitter(
        self, alias: str = "base", chunk_size: int = 1000, chunk_overlap: int = 100
    ) -> types.TextSplitter:
        if alias == "base":
            return RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", " ", ""],  # default
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,  # default
                is_separator_regex=False,  # defalult
            )
        elif alias == "char":
            return CharacterTextSplitter(
                separator="\n\n",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
        else:
            raise Exception("Value not found")


class RetrievalBuilder(VectorstoreBuilder):
    async def make_llm(self, llmDTO: LlmDTO) -> types.BaseLanguageModel:
        callbacks = self.make_callbacks()

        if llmDTO is None:
            raise InvalidRequestException("model_name", error_code=ErrorCode.NOT_EXIST)

        if llmDTO.llm_type == "openai":
            return ChatOpenAI(
                model=llmDTO.llm_name,
                temperature=llmDTO.temperature,
                api_key=llmDTO.api_key,
                streaming=llmDTO.streaming,
                callbacks=callbacks,
            )
        elif llmDTO.llm_type == "sds":
            return HuggingFaceTextGenInference(
                inference_server_url=llmDTO.inference_server_url,
                max_new_tokens=llmDTO.max_new_tokens,
                top_k=llmDTO.top_k,
                top_p=llmDTO.top_p,
                typical_p=llmDTO.typical_p,
                temperature=llmDTO.temperature,
                repetition_penalty=llmDTO.repetition_penalty,
                streaming=llmDTO.streaming,
                callbacks=callbacks,
            )
        else:
            raise InvalidRequestException("llm model", ErrorCode.NOT_EXIST)

    def make_callbacks(self) -> list[types.BaseCallbackHandler]:
        callbacks: list[types.BaseCallbackHandler] = []
        stream_log: bool = self.config.base.stream_log()
        if stream_log:
            callbacks.append(StreamingStdOutCallbackHandler())
        token_usage_log: bool = self.config.base.token_usage_log()
        if token_usage_log:
            callbacks.append(TokenMetricsCallbackHandler())
        return callbacks


class TokenEncoderBuilder(FeatureBuilder):
    def make_token_encoder(self, model_name: str) -> types.TokenEncoder:
        engine = SupportedModels.LLM.get(model_name, None)
        if engine == "openai":
            tokenizer = tiktoken.encoding_for_model(model_name)
            return tokenizer.encode
        elif engine == "sds":  # TODO: 테스트 필요
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            return tokenizer.encode
        else:
            raise InvalidRequestException("tokenizer model", ErrorCode.NOT_EXIST)


class FeatureDirector(ABC): ...


class ServiceDirector(FeatureDirector):
    @inject
    async def build_retrieval_service(
        self,
        user_id: str,
        collection_name: str,
        embedding_model_name: str,
        llm_model_name: str,
        alias: str = "base",
        builder: RetrievalBuilder = Provide["retrieval_builder"],
        llm_service: LlmService = Provide["llm_service"],
    ) -> RetrievalService:
        embedding, llmDTO = await asyncio.gather(
            builder.make_embedding(embedding_model_name),
            llm_service.get_llm(user_id, llm_model_name),
        )
        vectorstore, llm = await asyncio.gather(
            builder.make_vectorstore(collection_name, embedding),
            builder.make_llm(llmDTO),
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
        builder: VectorstoreBuilder = Provide["vectorstore_builder"],
    ) -> EmbeddingService:
        embedding = await builder.make_embedding(embedding_model_name)
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return EmbeddingService(CollectionService(vectorstore))

    @inject
    async def build_collection_service(
        self,
        collection_name: str,
        builder: VectorstoreBuilder = Provide["vectorstore_builder"],
    ) -> CollectionService:
        embedding = SDSEmbedding()
        vectorstore = await builder.make_vectorstore(collection_name, embedding)
        return CollectionService(vectorstore)


class DocumentDirector(FeatureDirector):
    @inject
    async def build_splitted_document(
        self,
        file_path: str,
        extension: str,
        splitter_alias: str = "base",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        builder: DocumentBuilder = Provide["document_builder"],
    ) -> list[types.Document]:
        loader, text_splitter = await asyncio.gather(
            builder.make_loader(file_path, extension),
            builder.make_splitter(splitter_alias, chunk_size, chunk_overlap),
        )
        loaded_documents = loader.load()
        splitted_document = text_splitter.split_documents(loaded_documents)
        return splitted_document
