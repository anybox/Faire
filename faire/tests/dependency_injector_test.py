import pytest
from sqlalchemy.exc import IntegrityError

from faire.repository.user_repository_sqla import UserRepositorySQLA
from faire.tests.fixture import db_test


def test_UserRepositorySQLA(db_test):
    from faire.aggregate.user import User

    repository = UserRepositorySQLA(db_test.session)

    assert repository.get_all() == []
    repository.add(User(email="a@a.a"))
    assert len(repository.get_all()) == 1
    repository.add(User(email="a@b.a"))
    assert len(repository.get_all()) == 2

    repository.commit()


def test_UserRepositorySQLA_unique_email(db_test):
    from faire.aggregate.user import User

    repository = UserRepositorySQLA(db_test.session)

    repository.add(User(email="a@a.a"))
    repository.add(User(email="a@a.a"))

    with pytest.raises(IntegrityError):
        repository.commit()


def test_UserRepositorySQLA_find_by_id(db_test):
    from faire.aggregate.user import User

    repository = UserRepositorySQLA(db_test.session)

    user = User(email="a@a.a")
    repository.add(user)

    repository.commit()
    assert repository.find_by_id(user.id) is user
