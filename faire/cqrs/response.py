from typing import List, Any


class Response:
    """
    DTO used to wrap handlers responses
    """

    def __init__(
        self, payload: Any, errors: List[str] = [], infos: List[str] = []
    ):
        self.payload = payload
        self.errors = errors
        self.infos = infos

    def append_error(self, error: str):
        self.errors.append(error)

    def append_info(self, info: str):
        self.infos.append(info)
