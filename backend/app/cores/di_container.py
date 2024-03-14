from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Callable

from app.services.user_service import UserService
from app.repository import UserCrud
from app.cores.dependencies import (
    DocumentBuilder,
    RetrievalBuilder,
    ServiceDirector,
    DocumentDirector,
)


class DiContainer(DeclarativeContainer):
    # repositories
    user_crud = Singleton(UserCrud)

    # builders / directors
    _retrieval_builder = Singleton(RetrievalBuilder)
    _document_builder = Singleton(DocumentBuilder)
    _service_director = Singleton(ServiceDirector)
    _document_director = Singleton(DocumentDirector)

    # services
    user_service = Singleton(UserService, user_crud=user_crud)

    # (async) factories
    retrieval_service_factory = Callable(_service_director().build_retrieval_service)
    embedding_service_factory = Callable(_service_director().build_embedding_service)
    collection_service_factory = Callable(_service_director().build_collection_service)
    splitted_document_factory = Callable(_document_director().build_splitted_document)
