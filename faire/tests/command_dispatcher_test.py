from dataclasses import dataclass
from typing import List
from uuid import uuid4, UUID

import pytest

from faire.aggregate.user import User
from faire.command.command import CommandHandler, Command
from faire.command.user import RegisterUserHandler, RegisterUser
from faire.command_dispatcher import CommandDispatcher
from faire.repository import UserRepositoryInterface


def get_dispatcher(handler:CommandHandler) -> CommandDispatcher:
    dispatcher = CommandDispatcher()
    dispatcher.register_handler(handler)

    return dispatcher


class MookUserRepository(UserRepositoryInterface):
    """
    Dummy implementation of User repository
    """
    def __init__(self):
        self.users = {}

    def add(self, user: User) -> uuid4:
        user.id = uuid4()
        self.users[user.id] = user
        return user.id

    def find_by_id(self, id: uuid4) -> User:
        try:
            return self.users[id]
        except KeyError:
            raise ValueError(f"No user found with id {id}")

    def get_all(self) -> List[User]:
        return list(self.users.values())

class UnknownCommand(Command):
    """
    A Command our dispatcher should not
    """
    pass

def test_dispatch():

    # We create a handler and inject it with our dummy repository
    repository = MookUserRepository()
    handler = RegisterUserHandler(repository=repository)

    # Then we instanciate our dispatcher
    dispatcher = get_dispatcher(handler)

    # No user exist at this point
    assert repository.get_all() == []

    first_user_id = dispatcher.dispatch(RegisterUser(username="foo", email="bar"))

    # The dispatch should have created a user and returned its id
    assert isinstance(first_user_id, UUID)
    assert len(repository.get_all()) == 1

    # We should be able to retrieve our user
    assert isinstance(repository.find_by_id(first_user_id), User)


    with pytest.raises(ValueError):
        repository.find_by_id(uuid4())

    with pytest.raises(NotImplementedError):
        dispatcher.dispatch(UnknownCommand)









