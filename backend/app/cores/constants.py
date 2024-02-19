from enum import StrEnum

from .utils import as_posix


class ExtendedStrEnum(StrEnum):
    @classmethod
    def __list__(cls) -> list[str]:
        return [c.value for c in cls]


class BasePath(StrEnum):
    BACKEND = "backend"
    APP = as_posix(BACKEND, "app")
    CORES = as_posix(APP, "cores")
    DB = as_posix(APP, "database")
    MODELS = as_posix(APP, "models")
    ROUTERS = as_posix(APP, "routers")
    SCHEMAS = as_posix(APP, "schemas")
    SECRETS = as_posix(APP, "secrets")
    SERVICES = as_posix(APP, "services")
    QDRANT = as_posix(DB, "qdrant")
    ENVS = as_posix(BACKEND, "envs")


class Engines(ExtendedStrEnum):
    OPENAI = "openai"


class OpenaiEmbeddingModels(ExtendedStrEnum):
    LARGE_V3 = "text-embedding-3-large"
    SMALL_V3 = "text-embedding-3-small"
    V2_ADA = "text-embedding-ada-002"
