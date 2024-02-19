from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import BasePath
from .utils import as_posix


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir=BasePath.SECRETS,
    )
    OPENAI_API_KEY: str


class BaseEnvirons(Settings):
    env_root: str = BasePath.ENVS
    project_name: str = "KMG"


class BaseVectorStore(BaseSettings):
    env_root: str = BasePath.ENVS
    host: str = "localhost"
    port: int = 8000
    url: str = ":".join([host, str(port)])


class DevQdrantSettings(BaseVectorStore):
    model_config = SettingsConfigDict(
        env_file=as_posix(BaseVectorStore().env_root, "dev_qdrant.env"),
        env_prefix="QDRANT_",
    )


class DevSettings(BaseEnvirons):
    model_config = SettingsConfigDict(
        env_file=as_posix(BaseEnvirons().env_root, "dev.env")
    )


class RunSettings:
    def __init__(self, mode: str = "dev", vectorstore: str = "qdrant") -> None:
        self.mode = mode
        self.environ = self.get_environ()
        self.vectorstore = self.get_vectorstore(vectorstore)

    def get_environ(self) -> BaseEnvirons:
        if self.mode == "dev":
            return DevSettings()
        raise Exception("Wrong Options")

    def get_vectorstore(self, vectorestore: str) -> BaseVectorStore:
        if self.mode == "dev":
            if vectorestore == "qdrant":
                return DevQdrantSettings()
        raise Exception("Wrong Options")

    def print_dump(self) -> None:
        self._recurse_dump(self.__dict__)

    def _recurse_dump(self, D: dict[str, object], i: int = 0) -> None:
        for k, v in D.items():
            try:
                v.__dict__
                print("    " * i + f"{k}: {v.__class__.__name__}")
                self._recurse_dump(v.__dict__, i + 1)
            except:
                print("    " * i, end="")
                print(f"{k}={v}")


settings = RunSettings()
# settings.print_dump()
