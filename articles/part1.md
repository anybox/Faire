# Part 1 Let's dive in, shall we ?

### Method

I have a confession to make. I have struggle not being clueless when someone
explains something to me. Not that I'm dumb or anything (my mum says I'm 
special), rather, I have the attention span of a young hamster.

The way I like things explained to me is: going through __ONE__ concept, and
once I fully get it, building upon it. 

Here's how I'm going to proceed for every concept I'll tackle:
* Explain as clearly and thoroughly as possible 
* Write tests, to define specifications 
* Write the dummyest implementation possible to pass the tests
* Keep the proper implementation as a __TODO__ for future parts

### Core concepts (First batch)
#### Foreword

I'll go through the main concepts we'll use in this part.
Depending what your current familiarity with those concept is
at the moment, that may be a lot of information to process.

It'll become clearer at implementation.

#### Functional decomposition

When code began to be a thing, the only aim of coders was to make 
stuff work as intended.

While that's obviously still what you want for your code, things
have changed. Applications' complexity has grown exponentially and
unless the problem you want to solve is super simple (in which case
you're building a __script__ rather than an application), going heads
down and writing a fat blob of code will very quickly result in 
something totally unbearable.

(Side note: if you're interested in history of the idea of "clean 
code", this article is more or less its birth: 
[Goto statement considered harmful](https://homepages.cwi.nl/~storm/teaching/reader/Dijkstra68.pdf))


__Functional decomposition__ comes to ou rescue.

To put it simply, imagine your application as a set of __bricks__. 
Each brick should do ONE thing. Bricks are then used as the building 
block of more complex bricks and so on.


#### Unit test & TDD

To go a bit into technicalities (but that's a side note, you can skip it)
you have mainly two approach for a code to be tested:
* __Maths__: Your code can be proven right. Fun fact: that relies on 
programming paradigm (lambda calculus) that predates programming, even computer
* __Science__: Your code can (and that's waaaay more convenient than the 
previous approach) be tested with enough variety of inputs that it's fair to
assume it works as intended.

I have little -if any- clues about how to make provable code. We'll (as mostly
every one else using tests) go for the second.


So, to come back to our subject. A unit test is a function that will take one
of the aformentioned brick (a function). Give that function inputs, and test
whether or not it returns what we want it to return.

If you're not familiar yet with unit tests, don't panic, I'll detail each
step.

__TDD__ is the acronym of Test Driven Development. It simply describes the
process of writing the tests before what's to be tested.


#### Event Sourcing

To put it as simply as possible: let's say you're asked to code a wallet.
Specifications look something like that:
* When created, a wallet has a 0 balance
* Money can be added to the balance
* Money can be removed from the balance
* Balance can be queried

Classical approach would consist in something along the lines of
```python
class Wallet:
    def __init__(self):
        self.balance = 0

    def get_balance(self) -> float:
        return self.balance

    def deposit(self, amount:float) -> None:
        self.balance += amount

    def withdrawal(self, amount:float) -> None:
        if self.balance < amount:
            raise ValueError("Not enough")
        self.balance -= amount
```

Yes, it's a toy example. Obviously. In the real world there would be some
stuff with some kind of database, and some unique id.

But it's enough to highlight the core difference in the traditional approach
and event sourcing.

Well, the same (totally toy) thing, but event sourced would look something 
along those lines:

```python
class DepositEvent:
    def __init__(self, amount:float):
        self.amount = amount

class WithdrawalEvent:
    def __init__(self, amount:float):
        self.amount = amount
    

class Wallet:
    def __init__(self):
        self.events = []

    def get_balance(self) -> float:
        balance = 0
        for event in self.events:
            if isinstance(event, DepositEvent):
                balance += event.amount
            elif isinstance(event, WithdrawalEvent):
                balance -= event.amount

        return balance

    def deposit(self, amount:float) -> None:
        self.events.append( DepositEvent(amount=amount) )

    def withdrawal(self, amount:float) -> None:
        if self.get_balance() < amount:
            raise ValueError("Not enough")
        self.events.append( WithdrawalEvent(amount=amount) )
```

Pretty inelegant, and still not at all realworldy. But it's pretty much all
Event sourcing is about. An entity of some kind, in the traditional approach,
has a state. That state can be changed, arbitrarily.

Event sourcing is all about considering a state as a series of events. And
building a state we want by processing each time all the mutations induced
by events in the series.

Well, there is more to it. States can be persisted at some point of your
architecture, and squash events into checkpoints. 
Don't mind those details for now. It's just a reminder of the principle of
those articles: Complexity will be added gradually and the first steps won't
give you yet everything you need to actually use Event sourcing in a production
context. 

We'll get there eventually :)

#### Immutability

An immutable object is an object that state's is set as initialization, and
can't be affected afterward. Events are immutable.

#### Event

An __Event__ is an immutable object that materialize that stuff happened.
Like, you know... an event.

Broadly speaking, an __Event__ can be of several type and use, for instance
it can serve as a way of communicating between services.

In our case, and for now, we'll restrict ourselves to this definition:
> An __Event__ is the materialization of a mutation of an entity


#### Stream

When you gather events to build the state of an entity, you want only
events that affect this entity. A __Stream__ is just that. A set of events
for an entity. (Relationships will challenge a bit that definition, and 
we'll later talk about __Aggregates__ and __Domains__... Later)

#### Event Store

An __Event Store__ is like a __CRUD__ (Creat Read Update Delete) database, except 
for the __UD__ part. 

An __Event Store__ in a __CR__ database. Which is harder to say out loud.

For our first batch, we'll implement two methods: `add_event` and `get_stream`


### Implementation (of a TODO-list)

So, I'll repeat myself (I often do. I often do.) The first shots of code are
not real-world suitable. They're merely implementations of a naked concept.
They'll lack essential bits.

To be extra clear about that, as long as we're not into real-world territory 
I'll put in the header of all code file:
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
"""
```

#### Dependencies 

For now, we'll only have one: [rich](https://rich.readthedocs.io/en/latest/).
And it even has nothing to do with ES, it's a lib used to display stuff nicely


#### Create project structure

__Note for Python-nerds__: I won't go into virtual env details. Ideally you should 
always use one. Though my plan here is to use containers in further steps, so I won't
bother.

```shell script
mkdir -p faire/{events,tests,entities,utils}
touch faire/{.,events,tests,entities,utils}/__init__.py
touch faire/eventstore.py
touch faire/{events,entities}/todolist.py
touch faire/events/event.py
echo rich>>requirements.txt
echo pytest>>requirements.txt
python3 -m pip install -r requirements.txt
```

We'll call entities... entities. To avoid confusion with terminology.
We'll later refacto that when we'll talk about `projections` and `aggregates`
Don't worry about it for now.

#### Events
let's edit `faire/events/event.py`.

That will by our base event class every event will inherit from.
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
base class for events
"""
from dataclasses import dataclass

from faire.utils import PrettyDisplayMixin


@dataclass(frozen=True, repr=False)
class Event(PrettyDisplayMixin):
    """Base event class"""
    stream_id: str
```

We'll use builtin [dataclasses](https://docs.python.org/3/library/dataclasses.html)
If you've never used them it's pretty straightforward.

Events should be immutable (well, frozen, but that's good enough) and have
a `stream_id` field.

we'll just add a neat `__repr__` so it prints nicely, and put in a mixin

`faire/utils/pretty.py`
```python
import os
from rich.console import Console
from rich.table import Table


class PrettyDisplayMixin:
    def __repr__(self):
        table = Table(title=f"[bold red][[ {self.__class__.__name__} ]]")
        table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        table.add_column("Type", style="bold red on #000000")
        table.add_column("Value", justify="right", style="green")

        for attr, attr_type in self.__annotations__.items():
            table.add_row(
                attr, f"({attr_type.__name__})", str(getattr(self, attr))
            )

        console = Console(record=True, file=open(os.devnull, "w"))
        console.print(table)

        return str(console.export_text(styles=True))


__all__ = ["PrettyDisplayMixin"]
```

and in `faire/utils/__init__.py`
```python
from .pretty import PrettyDisplayMixin
```

(By the way, while pretty self explanatory, you don't have to bother 
understanding the code in `__repr__`. You'll be fine just going with it :) 

Oh, and while we're talking in parentheses, I'm a coder. I'm bad at making
stuff pretty :p )


Now let's take care of `faire/events/todolist.py`

For now, we want TodoLists to be created and we want to be able to add them
Tasks
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
Events related to TodoLists
"""
from dataclasses import dataclass

from faire.events.event import Event


@dataclass(frozen=True)
class TodoListCreated(Event):
    name: str


@dataclass(frozen=True)
class TaskAddedToBoard(Event):
    id: str
    name: str


__all__ = ["TodoListCreated", "TaskAddedToBoard"]
```

and in `faire/events/__init__.py`
```python
from .todolist import TodoListCreated, TaskAddedToBoard
```

__Note__: `***Created` is a bad naming practice in event sourcing. 
Though that's a topic for a future part :)


#### Entities

in `faire/entities/todolist.py` we'll create dead simple entities
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
TodoList entities
"""
from dataclasses import dataclass, field
from typing import List

from faire.utils import PrettyDisplayMixin


@dataclass(repr=False)
class Task(PrettyDisplayMixin):
    id: str
    name: str = None


@dataclass(repr=False)
class TodoList(PrettyDisplayMixin):
    id: str
    name: str = None
    tasks: List[Task] = field(default_factory=list)


__all__ = ["Task", "TodoList"]
```


#### Appliers

__Note to myself (and also TODO)__. I'm more used to the redux terminology,
where an event changes a state in a functional way thanks to `reducers`.

I believe the non-functional term is `applier`, but I've seen it called `handler`.
Which, for me, is what handles `Commands`. (so TODO).

We have our entities, our events, now we want events to actually do stuff to the entities.

An applier is a function that takes an entity and an event as parameter and returns
the entity enriched with what the event is supposed to do.

To use the exemple at the beginning of this article, that should look like:
```python
def depositApplier(event:MoneyDeposed, wallet:Wallet) -> Wallet:
    wallet.balance += event.amount
    return wallet
```

let's create our directory and files
```shell script
mkdir faire/appliers
touch faire/appliers/{__init__,todolist,applier}.py
```

The first step is to create an applier registry, so we can query the right one
to handle an event.

`faire/appliers/applier.py`
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
TodoList entities
"""
from typing import Callable

from faire.events.event import Event


class Applier:
    __appliers = {}

    @classmethod
    def register(cls, applier: Callable) -> Callable:
        """
        Decorator used to register appliers
        assumptions:
        * function prototype should look like `def bla(event:EventType, entity:EntityType) -> EntityType`
        * (For now) only one applier should be implemented per type of event
        :param applier:
        :return:
        """

        event_type = list(applier.__annotations__.values())[0]
        cls.__appliers[event_type] = applier

        return applier

    @classmethod
    def get_applier(cls, event: Event):
        def not_found_applier(event: Event, entity=None):
            raise ValueError(
                f"No applier found for event {event.__class__.__name__}"
            )

        return cls.__appliers.get(event.__class__, not_found_applier)


__all__ = ["Applier"]
```

then in `faire/appliers/todolist.py`
```python
"""
⚠ Toy implementation: not to be used in prod ⚠
"""
from faire.appliers.applier import Applier
from faire.entities import TodoList, Task
from faire.events import TodoListCreated, TaskAddedToList


@Applier.register
def create_todolist(event:TodoListCreated, todolist=None) ->TodoList:
    pass


@Applier.register
def add_task(event: TaskAddedToList, todolist:TodoList) -> TodoList:
    pass
    
```

### Making things work

You know what time it is kids ?

__It's time to write some tests !!__

![](./assets/happykids.jpg)

But first, let's recapitulate where we're at:
* We have a simple entity class `TodoList`

let's create and edit `faire/tests/appliers_test.py`

