"""Database configuration and connection helpers."""

from loguru import logger
from pathlib import Path

import duckdb
import pandas as pd
from pydantic import FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    """
    """

    model_config = SettingsConfigDict(
        env_file='config/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    data_file_name: Path
    table_name: str
    db_conn_str: str
    train_test_split_ratio: float
    train_table_name: str
    test_table_name: str


db_settings = DbSettings()  # type: ignore[call-arg]


class DatabaseCon:
    """_summary_
    """
    def __init__(self):
        self.db_conn_str = db_settings.db_conn_str

    def init_db(self, table_name: str, file_name: FilePath,) -> None:
        """
        """
        Path(self.db_conn_str).parent.mkdir(parents=True, exist_ok=True)

        with duckdb.connect(self.db_conn_str) as con:
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
