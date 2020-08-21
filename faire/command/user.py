from faire.aggregate.user import User
from faire.command.command import Command, CommandHandler
from faire.cqrs.response import Response
from faire.repository import UserRepositoryInterface


class RegisterUser(Command):
    username: str
    email: str


class RegisterUserHandler(CommandHandler, listen_to=RegisterUser):
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    def handle(self, command: RegisterUser) -> Response:

        id = self.repository.add(
            User(username=command.username, email=command.email)
        )

        return Response(payload=id)
