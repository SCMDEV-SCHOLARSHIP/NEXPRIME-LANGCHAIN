import logging
from fastapi.logger import logger as fastapi_logger
from app.cores.config import ConfigContianer as _ConfigContainer


logger = fastapi_logger

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

if _ConfigContainer.config.base.log_level() == "DEBUG":
    logger.setLevel(level=logging.DEBUG)
elif _ConfigContainer.config.base.log_level() == "INFO":
    logger.setLevel(level=logging.INFO)
elif _ConfigContainer.config.base.log_level() == "ERROR":
    logger.setLevel(level=logging.ERROR)
