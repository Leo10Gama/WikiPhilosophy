"""Module to handle logging information, because oh lawd there's a lot of logging to handle."""

import logging

formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(message)s')


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Function to create a Logger.
    
    Parameters
    ----------
    name: str
        The name of the logger.
    log_file: str
        The filepath to write the logging file to.
    level=logging.INFO
        The logger level.
    """

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
