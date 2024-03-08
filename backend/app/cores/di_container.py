from __future__ import annotations
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Self
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from app.cores.config import settings
import app.cores.common_types as types
from app.services.user_service import UserService
import app.services.retrieval_service as ret_serv
from app.repository import UserCrud
from app.database import ExtendedQdrant
from app.cores.constants import SupportedModels, SupportedVectorStores
from app.models.sds_embeddings import SDSEmbedding


# TODO: dependencies로 옮기기 + builder 분할(embedding 등)
class RetrievalServiceBuilder:  # TODO: director로 역할 변환
    def __init__(self, container) -> None:
        self.container = container  # TODO: 컨테이너에서 setting 받아오기

    def build_retrieval_service(
        self,
        llm_model_name: str,
        embedding_model_name: str,
        vectorstore_params: dict,
        choice: str = "openai-test",
    ) -> ret_serv.RetrievalService:
        llm = self.make_llm(llm_model_name)
        embedding = self.make_embedding(embedding_model_name)
        vectorstore = self.make_vectorstore(vectorstore_params)
        vectorstore._embeddings = embedding
        if choice == "openai-test":
            return ret_serv.OpenAIRetrievalService(vectorstore=vectorstore, llm=llm)
        else:
            raise Exception("Value not found")

    def make_vectorstore(self, params: dict) -> types.VectorStore:
        vs_name = settings.vectorstore.engine
        if vs_name == SupportedVectorStores.QDRANT:
            return ExtendedQdrant(**params)
        else:
            raise Exception("Value not found")

    def make_embedding(self, model_name: str) -> types.Embeddings:
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

    def make_llm(self, model_name: str) -> types.BaseLanguageModel:
        engine = SupportedModels.LLM.get(model_name, None)
        if engine == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            raise Exception("Value not found")


class DiContainer(DeclarativeContainer):
    __self__ = Self()
    config = Configuration()

    # repositories
    user_crud = Singleton(UserCrud)

    # services
    user_service = Singleton(UserService, user_crud=user_crud)

    # builder / director
    retrieval_service_builder = Singleton(RetrievalServiceBuilder, __self__)
