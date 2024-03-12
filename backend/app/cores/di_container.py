from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Singleton,
    Self,
    Callable,
)

from app.services.user_service import UserService
from app.repository import UserCrud
from app.cores.dependencies import DocumentBuilder, RetrievalBuilder, FeatureDirector


class DiContainer(DeclarativeContainer):
    __self__ = Self()
    config = Configuration()

    # repositories
    user_crud = Singleton(UserCrud)

    # builders / directors
    _retrieval_builder = Singleton(RetrievalBuilder)
    _documents_builder = Singleton(DocumentBuilder)
    feature_director = Singleton(FeatureDirector)

    # services
    user_service = Singleton(UserService, user_crud=user_crud)

    # (async) factories
    retrieval_service_factory = Callable(
        feature_director().build_retrieval_service, builder=_retrieval_builder
    )
    embedding_service_factory = Callable(
        feature_director().build_embedding_service, builder=_documents_builder
    )
    collection_service_factory = Callable(
        feature_director().build_collection_service, builder=_documents_builder
    )
    splitted_documents_factory = Callable(
        feature_director().build_splitted_documents, builder=_documents_builder
    )
