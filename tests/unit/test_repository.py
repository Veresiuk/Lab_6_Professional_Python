import pytest

from shop.exceptions import DuplicateProductError
from shop.repositories import InMemoryProductRepository


def test_repository_add_get_list(laptop):
    repo = InMemoryProductRepository()
    repo.add(laptop)
    assert repo.get("A-1") is laptop
    assert repo.list_all() == [laptop]


def test_repository_get_unknown_returns_none():
    assert InMemoryProductRepository().get("nope") is None


def test_repository_rejects_duplicates(laptop):
    repo = InMemoryProductRepository()
    repo.add(laptop)
    with pytest.raises(DuplicateProductError):
        repo.add(laptop)
