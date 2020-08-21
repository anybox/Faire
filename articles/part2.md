# Part 2: CQRS let's stat to build our actual application

## Where to start: Use cases

When you build a traditional CRUD application, it's common to start
by modeling your database schema.

Either with an ERM (Entity relationship models) modeling tools (as MySQL workbench)
or doing it as code by writing entities using your favorite ORM.

While nothing forbids that in the world of CQRS, __Use Cases__ are
a much better starting point.

So rather than

| __Customer__|
|--------------|

| column | type | 
|--------|------|
| id     | int  |
| email  | varchar(100) |
| address| ... |

(And so on...)

What your first step will look like should more be along the lines of:

> __As a customer I want to add articles to my basket__

That's where C and Q of CQRS come in:

Uses cases will reflect as interactions with the app

Those interactions will fall in one of two categories:

__Getting stuff__ (Query)

__Doing stuff__ (Command)

## What is this part going to be about

In this part we'll start implementing our application.

We'll do so with the CQRS architecture.
We won't use Event Sourcing, mixing those two yet would be confusing
and as you'll see, refactoring CQRS into CQRS+ES will be pretty 
straigthforward.

## Basic concepts
### DTO
A DTO (for Database Transfer Object) is a short lived object meant 
to contain data and carry it (Initially to a Database, but it's common
to refer to objects that fits this definition as DTO eventhough no DB is
involved.


### Entities and ValueObject

An entity is an object that as an identity, and represent an instance
of conceptual entities your application will use.

__Customer__ would be one.

A value object is conceptually close to an entity. The difference is
that a value object has no life cycle. And its identity is based on the
value(s) it wraps.

For instance a date, an amount of money, an address...
All those things should be considered equal by our system on the basis
of their value and type only.


### Command and Query

A command is simply a __DTO__, that will express an intention and contain data 
needed to perform the action intended. An action is whenever a mutation occurs

A query is pretty much the same thing, except its goal is to access data rather
than inducing a mutation


### Aggregate

An __Aggregate__ is an set of Entities and Values Objects that will collaborate
to represent a business concept.
That collaboration in insured by an object called __Aggregate Root__

An Aggregate root should be the only way object it contains may be accessed 
from outside.



## Functional concepts

Now we know what Queries and Commands and aggregates aree, we'll tackle concepts
of the architecture we'll use to implement those concepts.


### Handler

A Handler is the function associated with a command or a query (also events,
but that's for our next part)

### Repository

A repository is a class that implements an interface and take care of interactions
with the persistance layer of your application.

Since Interface are not a thing in Python you may wonder why and how. I'll get to
that in a bit.


## Let's get real

### Use cases

That's it guys we're actually coding our application !

Here are the use cases we'll want to implement in our first iteration:
* As a non-user I want to be able to register an account
* As an user I want to create TodoLists
* As an user with a TodoList, I want to add it tasks
* TodoLists should have:
    * A title
    * A description
    
* Tasks should have:  
    * A title
    * A description
    * A date of creation
    * A date at which the task should be done
    * A data at which MUST be done (which we'll call __deadline__)

We'll stick to that for now :)


### Architecture

Here's the first bits of code we're going to need
* [x] Base class for Aggregates
* [ ] Base class for Commands
* [ ] Base class for Handlers
* [x] A User Aggregate
* [ ] An interface for UserRepository
* [ ] A Dispatcher 

```shell script
mkdir faire/{aggregate,command,query,repository}
touch faire/{aggregate,command,query,repository}/{__init__,user}.py
touch faire/aggregate/aggregate.py
touch faire/command/command.py
```

`faire/aggregate/aggregate.py`
```python
from typing import Callable, NewType, Any
from uuid import uuid4

DefaultFactory = NewType("DefaultFactory", Callable[[], Any])


class Aggregate:
    """Base class for Aggregate with magic"""

    id: uuid4 = DefaultFactory(lambda :uuid4())
    
    def __init__(self, **kwargs):
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name in kwargs:
                setattr(self, attr_name, kwargs[attr_name])
                continue
            if isinstance(attr_type, DefaultFactory):
                setattr(self, attr_name, attr_type())
            if attr_type in (str, int, float):
                setattr(self, attr_name, getattr(self.__class__, attr_name))

```

`faire/aggregate/user.py`
```python

from faire.aggregate.aggregate import Aggregate

class User(Aggregate):
    username: str
    email: str
```

__NOTE__: __⚠__ username and email are typed as __strings__. This is a hugely
bad practice, and those should have their own types (That's where Value Objects
come in). For the sake of simplicity, we'll keep that as a __TODO__. But keep that
in mind.


`faire/command/command.py`
```python
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
        print(kwargs)
        # genre listen_to=...
        setattr(cls, "listen_to", kwargs["listen_to"])
        
    def handle(self, command:Command):
        raise NotImplementedError()

```

Our `Command` class is only used for typing

Command handler's job will be to handle commands (such a reveal :D )
One very important aspect is that command handlers should only have knowledge
of two things:
* The command (duh)
* Interfaces

In our case, the `Commands` that will have to do with __Users__ will only know
about `UserRepositoryInterface`

Let's write this class
`faire/repository/user.py`
```python
from uuid import uuid4
from typing import List

from faire.aggregates.user import User


class UserRepositoryInterface:
    def find_by_id(self, id: uuid4) -> User:
        raise NotImplementedError()

    def get_all(self) -> List[User]:
        raise NotImplementedError()

    def add(self, user: User) -> uuid4:
        raise NotImplementedError()
```

So, I say it again: 
__Handlers should only know they're dealing with an instance of an object
that implements a given Interface__

In other terms, the underlying database, persistance layer, ORM and so on,
those are no the concern of Handlers

`faire/command/user.py`
```python
from faire.aggregate.user import User
from faire.command.command import Command, CommandHandler
from faire.repository.user import UserRepositoryInterface


class RegisterUser(Command):
    username: str
    email: str


class RegisterUserHandler(CommandHandler, listen_to=RegisterUser):
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    def handler(self, command: RegisterUser):
        return self.repository.add(
            User(username=command.username, email=command.email)
        )
```

#### Dispatcher

Commands when arriving to our system, should be given to the proper handler

That's what the dispatcher is for.

```python
from collections import defaultdict

from faire.command.command import CommandHandler, NullHandler, Command


class CommandDispatcher:
    def __init__(self):
        self.handlers = defaultdict(NullHandler)

    def register_handler(self, handler: CommandHandler):
        self.handlers[handler.listen_to] = handler


    def dispatch(self, command:Command):
        return self.handlers[command.__class__].handle(command)
```


### Where we're at

We have enough elements to do two things:
* Start and have a board overview of our CQRS architecture
* Write some god damn test (It was said with a Texas accent. You can't say because it's text)

#### Architecture overview

Keep in mind we're still on mode "one bit of complexity at a time".
This is not prod ready yet.

Still, we can already write tests, make things happen, and TDD some implementations

Currently, what we have (and what we'll implement with TDD) looks something like this:
![assets/CQRS_archi_1.png](./assets/CQRS_archi_1.png) 

* __1 )__ Handlers are instanciated, and given their dependencies
    * (Their given instances of classes that implement interfaces they want. 
    In our case, __RegisterUserHandler__ should receive a class that implements
    __UserRepositoryInterface__). By the way, this is called __Collaborator Pattern__

* __2 )__ The dispatcher work is to receive a command and give it to the instance
of __Handler__ that matches its type

##### What questions hasn't been answered yet 
* How to handle authorisation and authentication (and more broadly, everything
inbetween command arriving to our system and its execution)
* How commands are made (essentially, how to make an application out of that,
with an API endpoint and so on)
* Everything about responses
* Pretty much everything about __Queries__

#### Let's write tests

`faire/tests/command_dispatcher_test.py`
```python
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
```

```shell script
pytest -s faire/tests/command_dispatcher_test.py
```

__❗ Tips__ Pytest's `-s` flag allows you to output stuff when running
tests. Which may come handy for debug.


