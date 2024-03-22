from pydantic import SecretStr, Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration

from app.cores.constants import BasePath
from app.cores.utils import as_posix


class SecretInfo(BaseSettings, extra="forbid"):
    model_config = SettingsConfigDict(
        secrets_dir=BasePath.SECRETS,
    )
    OPENAI_API_KEY: SecretStr = Field(default="", frozen=True)
    SDS_EMBEDDING_URL: SecretStr = Field(default="", frozen=True)
    SDS_LLAMA_URL: SecretStr = Field(default="", frozen=True)


class DataBaseInfo(BaseModel, extra="forbid"):
    url: str = Field(frozen=True)
    username: str = Field(frozen=True)
    password: str = Field(frozen=True)
    sql_log: bool = Field(frozen=True)


class VectorStoreInfo(BaseModel, extra="forbid"):
    engine: str = Field(frozen=True)
    host: str = Field(frozen=True)
    port: int = Field(frozen=True)
    url: str = Field(frozen=True)


class AuthenticationInfo(BaseModel, extra="forbid"):
    secret_key: SecretStr = Field(frozen=True)  # TODO: SecretInfo로 옮기기
    algorithm: str = Field(frozen=True)
    access_token_expire_minutes: int = Field(frozen=True)
    refresh_token_expire_hours: int = Field(frozen=True)
    issuer: str = Field(frozen=True)


class ApplicationInfo(BaseModel, extra="forbid"):
    project_name: str = "KMG"
    host: str = Field(frozen=True)
    port: int = Field(frozen=True)
    url: str = Field(frozen=True)
    log_level: str = Field(frozen=True)


class EnvironSettings(BaseSettings, extra="forbid"):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    base: ApplicationInfo
    db: DataBaseInfo
    vectorstore: VectorStoreInfo
    auth: AuthenticationInfo
    secrets: SecretInfo = SecretInfo()


class ConfigContianer(DeclarativeContainer):
    # config
    config = Configuration(
        default=EnvironSettings(
            _env_file=as_posix(BasePath.ENVS, "local.env")
        ).model_dump()
    )
