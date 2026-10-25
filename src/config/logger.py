from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='config/.env',
        env_file_encoding='utf-8',
    )

    log_level: str


def configure_logging(log_level: str) -> None:
    logger.remove()
    logger.add(
        'logs/app.log',
        rotation='1 day',
        retention='2 days',
        compression='zip',
        level=log_level,
    )


configure_logging(log_level=LoggerSettings().log_level)
