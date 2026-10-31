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
        file_name: str | Path | None = None,
    ):
        output_path = Path(file_name or self.file_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'Exporting data to {output_path}')
        dataframe.to_parquet(
            output_path, engine='pyarrow', compression='snappy'
        )
        logger.info('Export completed!')
        return dataframe, output_path

    def _save_feature_to_db(
            self,
            data_file_name: str | Path,
            query_string=None,
            table_name: str = db_settings.table_name,
    ):
        self.table_name = table_name
        self.file_name = data_file_name
        if query_string is None:
            self.query_string = f"""SELECT * FROM {self.table_name}"""
        else:
            self.query_string = query_string
        db.init_db(
            self.table_name,
            self.file_name,  # type: ignore[call-arg]
        )
        return db.query_to_df(self.query_string)

    def _split_data_as_train_test(self, dataframe: pd.DataFrame,):
        train_set, test_set = train_test_split(
            dataframe, test_size=db_settings.train_test_split_ratio
        )
        logger.info('Performed train test split on the dataframe.')
        logger.info(
            'Exited split_data_as_train_test method of Data_Ingestion().'
        )

        logger.info('Saving traning and test file to db')
        data_file_path = Path(self.file_name)
        train_file_name = data_file_path.with_name(
            f'{data_file_path.stem}_train.parquet'
        )
        test_file_name = data_file_path.with_name(
            f'{data_file_path.stem}_test.parquet'
        )
        _, train_file_name = self._export_data_into_feature_store(
            train_set, train_file_name
        )
        self._save_feature_to_db(
            data_file_name=train_file_name,
            table_name=db_settings.train_table_name,
        )
        _, test_file_name = self._export_data_into_feature_store(
            test_set, test_file_name
        )
        self._save_feature_to_db(
            data_file_name=test_file_name,
            table_name=db_settings.test_table_name,
        )

    def initiate_data_ingestion(self):
        dataframe = self._export_collection_as_parquet()
        _, data_file_name = self._export_data_into_feature_store(dataframe)
        dataframe = self._save_feature_to_db(data_file_name)
        self._split_data_as_train_test(dataframe)
