"""Shared fixtures."""
from __future__ import annotations

import pytest

from shop.config import Config
from shop.models import Product
from shop.repositories import InMemoryProductRepository
from shop.services import Catalog


@pytest.fixture
def laptop() -> Product:
    return Product("A-1", "Laptop", "electronics", 25000.0, 3)


@pytest.fixture
def sample_products(laptop: Product) -> list[Product]:
    return [
        laptop,
        Product("B-2", "Mouse", "electronics", 500.0, 20),
        Product("C-3", "Notebook", "stationery", 40.5, 100),
    ]


@pytest.fixture
def catalog(sample_products: list[Product]) -> Catalog:
    catalog = Catalog(InMemoryProductRepository(), Config(min_stock=5))
    for product in sample_products:
        catalog.add_product(product)
    return catalog


@pytest.fixture
def empty_catalog() -> Catalog:
    return Catalog(InMemoryProductRepository())


@pytest.fixture
def csv_file(tmp_path):
    """Temporary CSV file; removed message printed in teardown via yield."""
    path = tmp_path / "products.csv"
    path.write_text(
        "sku,name,category,price,quantity\n"
        "A-1,Laptop,electronics,25000,3\n"
        "B-2,Mouse,electronics,500,20\n"
        "C-3,Notebook,stationery,40.5,100\n",
        encoding="utf-8",
    )
    yield path
    path.unlink(missing_ok=True)
