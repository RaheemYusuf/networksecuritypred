"""Database configuration and connection helpers.

This module centralizes database configuration for the project and provides
a thin DuckDB wrapper for:
- creating tables from local data files (Parquet or other supported inputs),
- executing SQL queries, and
- returning query results as pandas DataFrames.

Configuration values are loaded from `config/.env` via Pydantic settings.
"""

import duckdb
import pandas as pd
from loguru import logger
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    """
    Database configuration settings for the application.

    Attributes:
        model_config (SettingsConfigDict): Model  config,
        loaded from .env file.
        data_file_name (Path): File system path for the data file. The file may
            be created later by the ingestion pipeline.
        table_name (str): Name of the table in the db.
        db_conn_str (str): Database connection string.
        train_test_split_ratio (float): The ratio for spliting data to
            test and train.
        train_table_name (str): Name of the train table.
        test_table_name (str): Name of the test table.
    """

    model_config = SettingsConfigDict(
        env_file='config/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    data_file_name: Path
    train_data_file_name: Path
    test_data_file_name: Path
    db_conn_str: str
    train_test_split_ratio: float
    table_name: str
    train_table_name: str
    test_table_name: str


db_settings = DbSettings()  # type: ignore[call-arg]


class DatabaseCon:
    """
    Setup and configure database for the app.

    This class provides the functionality to create a db using
    duckdb, insert a table, including train and test tables into
    it if it doesn't exist, and return a pandas dataframe.

    Attributes:
        self.db_conn_str: duckdb connection strings
        table_name: The name of table to be created.
        file_name: The parquet file to read the data from.
        file_source:
        query_string: external sql query to be run against the db.
        con: It helps to create a connection to the db and execute
            query
        query: query to be executed on the db

    Methods:
        init_db:  It initialise the db and creates the db object, and
            send query to the database.
        query_to_df (str):  queries the table in the database.
    """
    def __init__(self):
        self.db_conn_str = db_settings.db_conn_str

    def init_db(self) -> None:
        """
        It initialise the db and creates the db object, and
            send query to the database
        """
        self.table_list = [
            db_settings.table_name,
            db_settings.train_table_name,
            db_settings.test_table_name,
            ]
        self.file_list = [
            db_settings.data_file_name,
            db_settings.train_data_file_name,
            db_settings.test_data_file_name,
        ]
        Path(self.db_conn_str).parent.mkdir(parents=True, exist_ok=True)

        with duckdb.connect(self.db_conn_str) as con:
            for table_name, file_name in zip(
                self.table_list,
                self.file_list,
                strict=True
            ):
                logger.info(f'Creating table {table_name}')
                con.execute(f'DROP TABLE IF EXISTS {table_name}')
                file_source = (
                    f"read_parquet('{file_name}')"
                    if file_name.suffix == '.parquet'
                    else str(file_name)
                )
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} AS
                    SELECT * FROM {file_source}
                """
                con.execute(query)
                logger.info(f'{table_name} created.')

    def query_to_df(self, query_string: str) -> pd.DataFrame:
        """
        """
        with duckdb.connect(self.db_conn_str) as con:
            return con.sql(query_string).df()


db = DatabaseCon()
