from pythondi import Provider, configure

from app.repository import UserCrud, UserCrudImpl


def init_di():
    provider = Provider()
    provider.bind(UserCrud, UserCrudImpl)
    configure(provider=provider)