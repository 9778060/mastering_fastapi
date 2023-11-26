from functools import lru_cache
from typing import Optional
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    """Loads the dotenv file. Including this is necessary to get
    pydantic to load a .env file."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    USER: Optional[str] = None
    PASSWORD: Optional[str] = None
    ADDRESS: Optional[str] = None
    PORT: Optional[str] = None
    DATABASE: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    """Instantiate config based on the environment."""
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig
    }
    return configs.get(env_state, DevConfig)()

env_state = BaseConfig().ENV_STATE
config = get_config(env_state)
