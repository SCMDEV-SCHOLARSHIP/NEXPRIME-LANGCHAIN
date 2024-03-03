from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import BasePath
from .utils import as_posix


class SecretSettings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir=BasePath.SECRETS,
    )
    OPENAI_API_KEY: SecretStr = Field(frozen=True)
    SDS_EMBEDDING_URL: SecretStr = Field(frozen=True)


class EnvironInfo(BaseSettings, extra="forbid"):
    env_root: str = Field(default=BasePath.ENVS, frozen=True)
    project_name: str = "KMG"
    host: str = Field(frozen=True)
    port: int = Field(frozen=True)
    url: str = Field(frozen=True)
    db_url: str = Field(frozen=True)
    db_username: str = Field(frozen=True)
    db_password: str = Field(frozen=True)


class VectorStoreInfo(BaseSettings, extra="forbid"):
    engine: str
    env_root: str = Field(default=BasePath.ENVS, frozen=True)
    host: str = Field(frozen=True)
    port: int = Field(frozen=True)
    url: str = Field(frozen=True)


class DevQdrantSettings(VectorStoreInfo, extra="forbid"):
    model_config = SettingsConfigDict(
        env_file=as_posix(
            VectorStoreInfo.model_fields["env_root"].default, "dev_qdrant.env"
        ),
        env_prefix="QDRANT_",
    )
    engine: str = Field(default="qdrant", frozen=True)


class DevSettings(EnvironInfo, extra="forbid"):
    model_config = SettingsConfigDict(
        env_file=as_posix(EnvironInfo.model_fields["env_root"].default, "dev.env")
    )


class RunSettings:
    def __init__(self, mode: str = "dev", vectorstore: str = "qdrant") -> None:
        self._mode = mode
        self._environ = self._get_environ()
        self._vectorstore = self._get_vectorstore(vectorstore)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def environ(self) -> EnvironInfo:
        return self._environ

    @property
    def vectorstore(self) -> VectorStoreInfo:
        return self._vectorstore

    @property
    def OPENAI_API_KEY(self) -> str:
        return SecretSettings().OPENAI_API_KEY.get_secret_value()

    @property
    def SDS_EMBEDDING_URL(self) -> str:
        return SecretSettings().SDS_EMBEDDING_URL.get_secret_value()

    def _get_environ(self) -> EnvironInfo:
        if self.mode == "dev":
            return DevSettings()
        raise Exception("Wrong Options")

    def _get_vectorstore(self, vectorestore: str) -> VectorStoreInfo:
        if self.mode == "dev":
            if vectorestore == "qdrant":
                return DevQdrantSettings()
            else:
                raise Exception("Wrong Options")
        else:
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
