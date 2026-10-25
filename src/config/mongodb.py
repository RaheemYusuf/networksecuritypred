"""
"""
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient

# Dynamically find the .env file located in the same directory as this script
# CURRENT_DIR = Path(__file__).resolve().parent
# ENV_PATH = f'{CURRENT_DIR}/.env'


class MongodbSettings(BaseSettings):
    """
    """

    model_config = SettingsConfigDict(
        env_file='config/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    mongodb_uri: str


mongodb_settings = MongodbSettings()  # type: ignore[call-arg]


@logger.catch
def init_mongodb() -> None:
    """
    """

    uri = mongodb_settings.mongodb_uri
    client = MongoClient(uri)
    try:
        logger.info('Initiating connection to Mongodb...')
        client.admin.command('ping')
        print('Connected successfully')
        logger.info('Connected successfully.')
        client.close()

    except Exception as e:
        logger.exception(f'The following error occured: {e}')
        raise Exception(
            'The following error occurred: ', e)
