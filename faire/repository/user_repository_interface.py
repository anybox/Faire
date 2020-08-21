"""

"""
from uuid import uuid4

from faire.aggregates.user import User


class UserRepositoryInterface:
    def find_by_id(self, id: uuid4) -> User:
        raise NotImplementedError()

    def add(self, user: User) -> uuid4:
        raise NotImplementedError()


