import pandas as pd
from pathlib import Path
from loguru import logger
from sklearn.model_selection import train_test_split

from config import db, db_settings
from config import mongodb_settings, mongodb_init


class DataIngestion:
    """
    """
    def __init__(self) -> None:
        self.file_name = mongodb_settings.data_file_name

    def _export_collection_as_parquet(self):
        # 1. MongoDB connection
        db_name = mongodb_settings.data_ingestion_database_name
        collection_name = mongodb_settings.data_ingestion_collection_name
        self.mongo_client = mongodb_init.init_client()
        collection = self.mongo_client[db_name][collection_name]
        cursor = collection.find(
            {}, {"_id": 0}
        )  # Exclude _id to prevent typing error
        logger.info('Extracting and writing to Parquet...')

        # 2. Load data entirely into a Pandas DataFrame
        dataframe = pd.DataFrame(list(cursor))
        return dataframe

    def _export_data_into_feature_store(
        self,
        dataframe: pd.DataFrame,
        file_name: Path = mongodb_settings.data_file_name,
    ):
        self.file_name = file_name
        Path(self.file_name).parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'Exporting data to {self.file_name}')
        dataframe.to_parquet(
            self.file_name, engine='pyarrow', compression='snappy'
        )
        logger.info('Export completed!')
        return dataframe

    def _split_data_as_train_test(self, dataframe: pd.DataFrame,):
        train_file_name = mongodb_settings.train_data_file_name
        test_file_name = mongodb_settings.test_data_file_name

        train_set, test_set = train_test_split(
            dataframe, test_size=db_settings.train_test_split_ratio
        )
        logger.info('Performed train test split on the dataframe.')
        logger.info(
            'Exited split_data_as_train_test method of Data_Ingestion().'
        )

        self._export_data_into_feature_store(
            train_set, file_name=train_file_name
        )
        logger.info(f'Training data saved into {train_file_name}')

        self._export_data_into_feature_store(
            test_set, file_name=test_file_name
        )
        logger.info(f'Test data saved into {test_file_name}')

    def _save_feature_to_db(
        self,
        query_string: str | None = None,
        table_name: str | None = None,
    ) -> pd.DataFrame:
        if table_name is None:
            table_name = db_settings.table_name
        if query_string is None:
            query_string = f'SELECT * FROM {table_name}'
        db.init_db()
        return db.query_to_df(query_string)

    def initiate_data_ingestion(self):
        dataframe = self._export_collection_as_parquet()
        dataframe = self._export_data_into_feature_store(dataframe)
        self._split_data_as_train_test(dataframe)
        self._save_feature_to_db()
