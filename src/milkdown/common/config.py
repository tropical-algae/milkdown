import secrets

from pydantic_settings import BaseSettings


class SysSetting(BaseSettings):
    # FastAPI
    VERSION: str = "0.1.0"
    PROJECT_NAME: str = "EXAMPLE PROJECT"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # client
    VALID_CLIENT_VERSION: list[str] = ["0.X.X"]
    VALID_TIMESTAMP_DIFF: int = 300  # 时间验证允许的最大差值
    TRUSTED_DOMAINS: list[str] = ["127.0.0.1"]
    


class DBSetting(BaseSettings):
    # database
    SQL_DATABASE_URI: str = ""

    # user
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEFAULT_SUPERUSER: str = "admin"
    DEFAULT_SUPERUSER_PASSWD: str = "admin"
    
    # 
    VECTOR_STORE_URL: str = ""
    VECTOR_STORE_TOKEN: str = ""
    # VECTOR_STORE_NAMES: str = ""


class LogSetting(BaseSettings):
    # logger
    LOG_NAME: str = "log.test.record"
    LOG_PATH: str = "./log"
    LOG_FILE_LEVEL: str = "INFO"
    LOG_STREAM_LEVEL: str = "DEBUG"
    LOG_FILE_ENCODING: str = "utf-8"
    LOG_CONSOLE_OUTPUT: bool = True


class ServiceSetting(BaseSettings):
    # service
    GPT_PROMPT_TEMPLATE_PATH: str = ""
    GPT_BASE_URL: str = ""
    GPT_API_KEY: str = ""
    GPT_DEFAULT_MODEL: str = "gpt-3.5-turbo-ca"
    GPT_TEMPERATURE: float = 0.8
    GPT_RESPONSE_FORMAT: dict = {"type": "json_object"}
    
    EMBEDDING_BASE_URL: str = ""
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = "bge-m3"
    
    LOCAL_PROMPT_ROOT: str = "./documents/prompts"
    


class Setting(SysSetting, DBSetting, LogSetting, ServiceSetting):
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Setting()
