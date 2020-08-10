"""
⚠ Toy implementation: not to be used in prod ⚠
"""
from faire.appliers.applier import Applier
from faire.entities import TodoList, Task
from faire.events import TodoListCreated, TaskAddedToList


@Applier.register
def create_todolist(event: TodoListCreated, todolist=None) -> TodoList:
    if todolist is not None:
        raise ValueError(
            "This is an initializer, your entity should not exist at this point"
        )

    return TodoList(id=event.stream_id, name=event.name)


@Applier.register
def add_task(event: TaskAddedToList, todolist: TodoList) -> TodoList:
    todolist.tasks.append(Task(id=event.id, name=event.name))

    return todolist
