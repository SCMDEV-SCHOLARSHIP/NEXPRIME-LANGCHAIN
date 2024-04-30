from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Callable, Aggregate

from app.cores.constants import BasePath
from app.cores.utils import as_posix
from app.cores.logger import LoggerMaker

from app.services.user_service import UserService
from app.services.file_service import FileService
from app.services.auth_service import (
    AuthService,
    DefaultValidationStrategy,
    IgnoreExpiredValidationStrategy,
    ExpiredYetValidationStrategy,
)
from app.services.login_service import LoginService, FormBaseLoginStrategy
from app.services.history_service import (
    MemoryHistoryService,
    NoMemoryStrategy,
    BufferMemoryStrategy,
    BufferWindowMemoryStrategy,
    SummaryMemoryStrategy,
)

from app.database.rdb.session import AsyncSessionManager
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
    _logger_maker = Singleton(LoggerMaker)
    logger = _logger_maker.provided.logger
    session_mgr = Singleton(AsyncSessionManager)
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
    login_service = Singleton(LoginService)
    history_service = Singleton(MemoryHistoryService)

    # (async) factories
    retrieval_service_factory = Callable(_service_director().build_retrieval_service)
    embedding_service_factory = Callable(_service_director().build_embedding_service)
    collection_service_factory = Callable(_service_director().build_collection_service)
    splitted_document_factory = Callable(_document_director().build_splitted_document)

    # strategies
    login_strategy = Aggregate(
        form_base=Singleton(FormBaseLoginStrategy),
    )
    token_validation_strategy = Aggregate(
        default=Singleton(DefaultValidationStrategy),
        ignore_expired=Singleton(IgnoreExpiredValidationStrategy),
        expired_yet=Singleton(ExpiredYetValidationStrategy),
    )
    memory_strategy = Aggregate(
        nothing=Singleton(NoMemoryStrategy),
        buffer=Singleton(BufferMemoryStrategy),
        buffer_window=Singleton(BufferWindowMemoryStrategy),
        summary=Singleton(SummaryMemoryStrategy),
    )
