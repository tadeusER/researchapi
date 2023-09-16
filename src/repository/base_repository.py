from utils.logger import get_logger


class BaseRepository:

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = get_logger(self.source_name)

    def query(self, query_string: str):
        self._debug(f"Querying {self.source_name} with: {query_string}")

    def _debug(self, message: str):
        self.logger.debug(message)