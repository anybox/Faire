from faire.cqrs.response import Response


class Command:
    """
    base class for commands
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:
        Set attr from kwargs
        # Note: This is still yet a toy, non-prod-ready mechanism
        """
        for attr_name in self.__annotations__:
            setattr(self, attr_name, kwargs.get(attr_name))


class CommandHandler:
    """
    Base class for Command Handlers
    :use:
    ```python3
    # Assuming a command FooCommand
    class FooCommandHandler(CommandHandler, listen_to=FooCommand):
        def __init__(self, repository:FooRepositoryInterface):
            self.repository = repository

        def handle(self, command:FooCommand):
            ...
    ```
    """

    def __init_subclass__(cls, **kwargs):
        setattr(cls, "listen_to", kwargs.get("listen_to"))

    def handle(self, command: Command) -> Response:
        raise NotImplementedError(
            f"No handler registred for {command.__class__.__name__}"
        )


class NullHandler(CommandHandler, listen_to=Command):
    """
    Default handler, when a command has no handler registred, this one
    will be used and raise an error
    """
