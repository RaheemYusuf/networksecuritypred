"""
MongoDB configuration and connection helpers.

This module centralises MongoDB configuration for the project and provides
functionalities for:
- innitialisation of the MongoDB database config details
"""

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient


class MongodbSettings(BaseSettings):
    """
    MongoDB database configuration settings for the application.

    Attributes:
        model_config (SettingsConfigDict): Model config,
        loaded from .env file.
        mongodb_uri (str): MongoDB connection strings.
        data_ingestion_collection_name (str): MongoDB database collection name.
        dat_ingestion_database_name (str): MongoDB database name.
    """

    model_config = SettingsConfigDict(
        env_file='config/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    mongodb_uri: str
    data_ingestion_collection_name: str
    data_ingestion_database_name: str


mongodb_settings = MongodbSettings()  # type: ignore[call-arg]


class MongodbInit:
    """
    Initialisation of the MongoDB Client

    This class provides the functionality to initialise the MongoDB database.

    Attribute:
        uri: MongoDB connection string.

    Method:
        init_mongodb_client: It initialises the mongodb db and create a client
        for mongodb connection.
    """
    @logger.catch
    def init_mongodb_client(self):
        """It initialises the mongodb db and create a client
        for mongodb connection.

        Returns:
            mongodb client.
        """
        uri = mongodb_settings.mongodb_uri
        client = MongoClient(uri)
        try:
            logger.info('Initiating connection to Mongodb...')
            client.admin.command('ping')
            logger.info('Connected successfully.')
            return client

        except Exception as e:
            client.close()
            logger.exception(f'The following error occured: {e}')
            raise Exception(
                'The following error occurred: ', e)


mongodb_init = MongodbInit()
