import logging
from logging.handlers import RotatingFileHandler
from config.settings import LOG_DIR

def get_logger(name:str) -> logging.Logger:
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    log_dir=LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter=logging.Formatter("%(asctime)s |%(levelname)s |%(name)s|%(message)s") 

    file_handler = RotatingFileHandler(
        log_dir / "pipeline.log",
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
