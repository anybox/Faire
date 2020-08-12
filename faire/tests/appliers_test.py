from faire.events import TodoListCreated, TaskAddedToList
from faire.entities import TodoList, Task
from faire.appliers import Applier
from faire.appliers.todolist import create_todolist, add_task


def test_get_appliers():
    assert (
        Applier.get_applier(TodoListCreated(stream_id="foo", name="bar"))
        is create_todolist
    )

    assert (
        Applier.get_applier(
            TaskAddedToList(stream_id="foo", id="baz", name="bar")
        )
        is add_task
    )


def create_todolist():
    mock_stream = [
        TodoListCreated(stream_id="foo", name="test_todolist"),
        TaskAddedToList(stream_id="foo", id="foo_bar", name="my first task !"),
        TaskAddedToList(stream_id="foo", id="far_boo", name="my second task !"),
    ]

    expected_todolist = TodoList(id="foo",
                                 name="test_todolist",
                                 tasks=[
                                     Task(id="foo_bar", name="my first task !"),
                                     Task(id="far_boo", name="my second task !"),
                                 ])

    


