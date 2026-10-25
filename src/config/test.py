from loguru import logger


@logger.catch
def test_exception():
    try:
        logger.info('Entering the try block')
        a = 1/0
        print('This will be printed', a)
    except Exception as e:
        logger.exception(f'{e}')


@logger.catch
def test_logger_exception():
    logger.info('Entering the try logger exception')
    a = 1/0
    print(f'This will be printed {a}')
