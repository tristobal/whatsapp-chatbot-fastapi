import logging
from app.core.config import settings

def setup_logging():
    logger = logging.getLogger(settings.APP_NAME)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logging()