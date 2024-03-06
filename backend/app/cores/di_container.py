from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton
from app.services.user_service import UserService
from app.repository import UserCrud


class DiContainer(DeclarativeContainer):
    config = Configuration()

    # repositories
    user_crud = Singleton(UserCrud)

    # services
    user_service = Singleton(UserService, user_crud=user_crud)
