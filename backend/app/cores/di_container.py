from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Callable

from app.cores.constants import BasePath
from app.cores.utils import as_posix
from app.cores.logger import SDSLoggerMaker

from app.services.user_service import UserService
from app.services.file_service import FileService
from app.services.auth_service import AuthService

from app.database.rdb.session import SDSAsyncSessionManager
from app.repository import UserCrud, JWTTokenCrud, FileCrud

from app.cores.dependencies import (
    VectorstoreBuilder,
    DocumentBuilder,
    RetrievalBuilder,
    ServiceDirector,
    DocumentDirector,
)


class DiContainer(DeclarativeContainer):
    # base
    config = Configuration(
        yaml_files=[
            as_posix(BasePath.ENVS, "application.yaml"),
            as_posix(BasePath.ENVS, "local.yaml"),
            as_posix(BasePath.SECRETS, "secret.yaml"),
        ],
    )
    _logger_maker = Singleton(SDSLoggerMaker)
    logger = _logger_maker.provided.logger
    session_mgr = Singleton(SDSAsyncSessionManager)
    session = session_mgr.provided.session

    # repositories
    user_crud = Singleton(UserCrud)
    file_crud = Singleton(FileCrud)
    token_crud = Singleton(JWTTokenCrud)

    # builders / directors
    _vectorstore_builder = Singleton(VectorstoreBuilder)
    _retrieval_builder = Singleton(RetrievalBuilder)
    _document_builder = Singleton(DocumentBuilder)
    _service_director = Singleton(ServiceDirector)
    _document_director = Singleton(DocumentDirector)

    # services
    user_service = Singleton(UserService, user_crud=user_crud)
    file_service = Singleton(FileService, file_crud=file_crud, user_crud=user_crud)
    auth_service = Singleton(AuthService, token_crud=token_crud)

    # (async) factories
    retrieval_service_factory = Callable(_service_director().build_retrieval_service)
    embedding_service_factory = Callable(_service_director().build_embedding_service)
    collection_service_factory = Callable(_service_director().build_collection_service)
    splitted_document_factory = Callable(_document_director().build_splitted_document)
