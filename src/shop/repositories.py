"""Product repository implementations."""
from __future__ import annotations

from shop.exceptions import DuplicateProductError
from shop.models import Product


class InMemoryProductRepository:
    """Simple repository storing products in a dictionary."""

    def __init__(self) -> None:
        self._items: dict[str, Product] = {}

    def add(self, product: Product) -> None:
        if product.sku in self._items:
            raise DuplicateProductError(f"Product {product.sku} already exists")
        self._items[product.sku] = product

    def get(self, sku: str) -> Product | None:
        return self._items.get(sku)

    def list_all(self) -> list[Product]:
        return list(self._items.values())
