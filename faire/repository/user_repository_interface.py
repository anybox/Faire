"""

"""
from typing import List
from uuid import uuid4

from faire.aggregate.user import User


class UserRepositoryInterface:
    def find_by_id(self, id: uuid4) -> User:
        raise NotImplementedError()

    def get_all(self) -> List[User]:
        raise NotImplementedError()

    def add(self, user: User) -> uuid4:
        raise NotImplementedError()




