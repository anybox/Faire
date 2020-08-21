from typing import List
from uuid import uuid4

from faire.aggregate.user import User
from faire.repository import UserRepositoryInterface


class UserRepositoryPickle(UserRepositoryInterface):
    def find_by_id(self, id: uuid4) -> User:
        pass

    def get_all(self) -> List[User]:
        pass

    def add(self, user: User) -> uuid4:
        pass
