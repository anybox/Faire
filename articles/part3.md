
#### Refacto our entities

______________________
à ce stade c'est des notes des trucs que j'ai fait
`mv faire/entities faire/aggregates`

##### Aggregate

You may have noticed that in the first part, appliers were in their
own directory.

This was for the sake of clarity rather than anything with architectural 
rational (which I'm not saying can't be the case in some contexts).

Now we work with `Aggregates`, let's be a bit more rigorous on which object
has which responsibilities.

Here's what we want to achieve:
```python
#assumption my_todolist is an instance of TodoList
my_todolist.apply(TaskAddedToList(id="foo", ...)) 
```

```python
from typing import Callable, NewType
from uuid import uuid4

from faire.events.event import Event


DefaultFactory = NewType('DefaultFactory', Callable[[], Any])

def applier(
    event_type,
) -> Callable[[Callable[[Event,], None],], Callable[[Event,], None]]:
    """
    Decorator. Use it to register an applier for an EventType in a given class
    
    .. code-block:: python
        class MyAggregate(Aggregate):
            @applier(SomeEventType)
            def method_that_will_do_stuff(self, event:SomeEventType) -> None:
                ... # Here come some mutations
                print("hey")
                
        # Then this will work
        
        #vars :`my_aggregate` assumed type is `MyAggregate`
        #      `some_event` assumed type is `SomeEventType`
        
        my_aggregate.apply(some_event) # prints "hey"
        
    `
    :param event_type: class of event to be matched by decorated method
    :type event_type: type
    :return: The same method
    ____________
    # TODO
    ## Refacto types
    
    Callable[[Event], None] Could probably be cleaner with the use of
    typing.NewType, somehow. 
    Signature of this decorator (especialy return type
    (-> Callable[[Callable[[Event,], None],], Callable[[Event,], None]])
    is confusing 
    """

    def _decorator(method: Callable[[Event], None]) -> Callable[[Event], None] :
        setattr(method, "applier_for", event_type)
        return method

    return _decorator


class Aggregate:
    """Base class for Aggregate with magic"""
    version: int = 1

    def __init__(self, id: uuid4):
        self.id: uuid4 = id
        
        for attr_name, attr_type in self.__annotations__.items():
            if isinstance(attr_type, DefaultFactory):
                setattr(self, attr_name, attr_type())
            if attr_type in (str, int, float):
                setattr(self, attr_name, getattr(self.__class__, attr_name))

    def _null_applier(self, event:Event) -> None:
        """
        Null Object Pattern. It's the applier used when an unmatched event is 
        received. Its only aim is to raise a ValueError
        
        :param event: 
        :raises: ValueError
        """
        raise ValueError(
            f"No applier registrer for {event.__class__.__name__}"
            f" in {self.__class__.__name__}"
        )

    def __init_subclass__(cls, **kwargs):
        """
        Here are registered all the appliers when a class's MRO is set
        """
        cls._appliers = {}
        for member in cls.__dict__.values():
            if hasattr(member, "applier_for"):
                cls._appliers[member.applier_for] = member

    def apply(self, event:Event) -> None:
        """
        Dispatch an Event according to its type to the appropriate
        :param event: 
        :type event: Event
        """
        self._appliers.get(event.__class__, self._null_applier)(self, event)
        self.version += 1
        

```

That's how.
Don't worry, I'm going to break that code down

First we want an `Aggregate` base class. We'll assume for now that
we'll want every aggregate to have an `id` (of type `uuid4`) and a version
number which will increment every time a mutation is done.

The `applier` method on top is a decorator. Its role is to bind a given
type of event to a given method.

The binding is taken care of in `Aggregate.__init_subclass__` method

It's now straightforward to add appliers to our aggregates

 mkdir -p faire/{commands,queries}   
 touch faire/{commands,queries}/__init__.py
 
#### Use cases, command and queries

Rather than Modeling our database, we're going to think about use cases.

We can distinguish interactions with an application by their intention in two
categories:
* Queries (intention is to have an information)
* Command (intention is to do stuff)

`faire/commands/command.py`
```python

class Command:
    """
    base class for commands
    """


class Handler:
    """
    base class for command handler
    """
    def __init_subclass__(cls, **kwargs):
        setattr(cls, "listen_to", kwargs["listen_to"])
```


We'll first code as if we weren't using event sourcing. Then we'll add it


`faire/commands/user.py`
```python
from faire.commands.command import Command
class CreateUser(Command):
    pass
```

It's time we have that talk... about why `***Created` may often
be a bad naming practice.

In DDD (Domain Driven Design), the words you'll use in your code should
be the same as those you'll express your use cases with.

More importantly, those world should have as much of a specific, domain
meaning as possible.

This example is trivial, but you should always ask yourself if meaningful
domain terminology would fit in place of generic language.

When you say `UserCreated`... I mean... Did you ?
Was this poor user lying in nothingness before that operation ?


You'll agree `RegisterNewUser` makes more real-world sense:

so...
`faire/commands/user.py`
```python
from faire.commands.command import Command
class RegisterNewUser(Command):
    username: str
    email: str
    password: str
```

#### Command Handlers

Now we have that command, we want a command handler, to implement
behaviour to our application to have when the command occurs.
___________
##### If you're in panic

You may at this point be a bit overwhelmed by the amount of 
kinds of objects. 

You may also wonder WHEN and HOW a command occurs.
Who calls the handlers ? What listen to what ?

Those are rightful questions. Don't worry, we'll go into that
_____________

Interfaces are not a thing in Python
Also, we delibertly took the side of systematicaly naming our 
objects without their kind as a suffix 
(That would have looked like: UserRegisteredEvent, RegisterUserCommand...)

That said, in the particular place, I want somehow to make extra clear that
the intention is to separate specification from implementation.

Also, we'll somehow enforce it rather than just naming our class with 
`Interface` suffix and trusting dev to kindly respect the good practices 
invoked.

When you think about software as an architect, don't trust dev.

The way I personally do that, is by starting to especially not trust my
dev-self.

Here are two of the top 10 biggest lies of mankind according to a very
serious study I've just made up.

> "I'll just close my eyes 5 more minutes. I won't sleep"


> "I'll fix that monkey patch later"


So, we'll have to emulate somehow interface and the constraints they impose on
code writting.

Using the fact mypy checks Liskov substitution principle is respected is
convenient. We'll use that... in... later parts.

For now... well... we'll do with trust (we'll succeed, thanks to the power of
frienship !)


Wait... Weren't we talking about command handlers ?

Right
```python
class RegisterNewUserHandler(Handler, listen_to=RegisterNewUser):
    def __init__(self, repository:UserRepositoryInterface):
        self.repository = repository

    def handle(self, command:RegisterNewUser):
        pass
```

