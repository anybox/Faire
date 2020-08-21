from collections import defaultdict

from faire.command.command import CommandHandler, NullHandler, Command


class CommandDispatcher:
    def __init__(self):
        self.handlers = defaultdict(NullHandler)

    def register_handler(self, handler: CommandHandler):
        self.handlers[handler.listen_to] = handler


    def dispatch(self, command:Command):
        return self.handlers[command.__class__].handle(command)

