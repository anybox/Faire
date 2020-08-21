from collections import defaultdict
from typing import List

from faire.command.command import CommandHandler, NullHandler, Command
from faire.cqrs.middleware import CommandMiddlewareBus
from faire.cqrs.response import Response


class CommandDispatcher:
    def __init__(self):
        self.handlers = defaultdict(NullHandler)

    def register_handlers(self, handlers: List[CommandHandler]):
        bus = CommandMiddlewareBus(handlers)
        self.handlers[bus.listen_to] = bus

    def dispatch(self, command: Command) -> Response:
        return self.handlers[command.__class__].handle(command)
