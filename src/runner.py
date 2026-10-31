from components import DataIngestion
from config import db, db_settings
from loguru import logger


@logger.catch
def main():
    DataIngestion().initiate_data_ingestion()
    logger.info('starting query')
    query = f"""SELECT COUNT(*) FROM {db_settings.table_name}"""
    query1 = db.query_to_df(query)
    logger.info(f'query1 result {query1}')
    query = f"""SELECT COUNT(*) FROM {db_settings.train_table_name}"""
    query2 = db.query_to_df(query)
    logger.info(f'query1 result {query2}')


if __name__ == '__main__':
    main()
