"""Interfaces of external dependencies."""
from __future__ import annotations

from typing import Protocol

from shop.models import Product


class ProductRepository(Protocol):
    def add(self, product: Product) -> None: ...
    def get(self, sku: str) -> Product | None: ...
    def list_all(self) -> list[Product]: ...


class Notifier(Protocol):
    def notify(self, message: str) -> None: ...


class DiscountProvider(Protocol):
    def get_discount(self, category: str) -> float: ...


class PriceProvider(Protocol):
    async def fetch_price(self, sku: str) -> float: ...
