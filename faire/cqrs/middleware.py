from __future__ import annotations
from typing import List, Union

from toolz import sliding_window

from faire.command.command import CommandHandler


class CommandMiddleware:
    """
    Base class for Command Middlewares
    :use:
    ```python3
    class LoggingTimeHandler(CommandHandler, CommandMiddleware):
          def __init__(self, logger:LoggerInterface):
              self.logger = logger

          def handle(self, command:Command):
              start_time = time()
              response = self.next.handle(command)
              exec_time= time() - start_time
              self.logger.log(f"exec time: {exec_time}")

              return response
    """

    def set_next(self, next_: Union[CommandMiddleware, CommandHandler]):
        """
        Sets the handler comming next to create a chain
        :param next_:
        :return:
        """
        self.next = next_


class CommandMiddlewareBus:
    """
    Bus, that handle proper execution of middlewares to handle a command

    :use:
    ```python3
    bus = CommandMiddlewareBus([middleware1, middleware2, finalhandler])

    bus.handle(some_command)

    ```
    """

    def __init__(
        self, handlers: List[Union[CommandMiddleware, CommandHandler]]
    ):
        for current_middleware, next_middleware in sliding_window(2, handlers):
            current_middleware.set_next(next_middleware)

        self.handle = handlers[0].handle
        self.listen_to = handlers[-1].listen_to
