import logging
from fastapi.logger import logger as fastapi_logger
from dependency_injector.wiring import inject, Provide


class SDSLoggerMaker:
    def __init__(self) -> None:
        self.logger = fastapi_logger
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(self.handler)

    @inject
    def set_level(self, log_level: str = Provide["config.base.log_level"]) -> None:
        if log_level == "DEBUG":
            self.logger.setLevel(level=logging.DEBUG)
        elif log_level == "INFO":
            self.logger.setLevel(level=logging.INFO)
        elif log_level == "ERROR":
            self.logger.setLevel(level=logging.ERROR)
