"""Business logic of the shop."""
from __future__ import annotations

from shop.config import Config
from shop.exceptions import ExternalServiceError, ProductNotFoundError
from shop.models import Product
from shop.protocols import DiscountProvider, Notifier, ProductRepository


class Catalog:
    """Product catalog working on top of a repository."""

    def __init__(self, repository: ProductRepository, config: Config | None = None) -> None:
        self._repository = repository
        self._config = config or Config()

    def add_product(self, product: Product) -> None:
        self._repository.add(product)

    def all_products(self) -> list[Product]:
        return self._repository.list_all()

    def find_product(self, sku: str) -> Product:
        product = self._repository.get(sku)
        if product is None:
            raise ProductNotFoundError(f"Product {sku} not found")
        return product

    def search_by_name(self, text: str) -> list[Product]:
        needle = text.strip().lower()
        return [p for p in self._repository.list_all() if needle in p.name.lower()]

    def filter_by_category(self, category: str) -> list[Product]:
        wanted = category.strip().lower()
        return [p for p in self._repository.list_all() if p.category.lower() == wanted]

    def total_stock_value(self) -> float:
        return sum(p.stock_value for p in self._repository.list_all())

    def most_expensive(self) -> Product | None:
        return max(self._repository.list_all(), key=lambda p: p.price, default=None)

    def low_stock_products(self) -> list[Product]:
        return [p for p in self._repository.list_all() if p.quantity < self._config.min_stock]


class PricingService:
    """Calculates discounted prices using an external discount provider."""

    def __init__(self, provider: DiscountProvider) -> None:
        self._provider = provider

    def discounted_price(self, product: Product) -> float:
        try:
            percent = self._provider.get_discount(product.category)
        except Exception as exc:
            raise ExternalServiceError("Discount provider failed") from exc
        if not 0 <= percent <= 100:
            raise ExternalServiceError(f"Invalid discount: {percent}")
        return product.price * (1 - percent / 100)


class StockMonitor:
    """Sends notifications about products with low stock."""

    def __init__(self, catalog: Catalog, notifier: Notifier) -> None:
        self._catalog = catalog
        self._notifier = notifier

    def check(self) -> int:
        low = self._catalog.low_stock_products()
        for product in low:
            self._notifier.notify(f"Low stock: {product.sku} ({product.quantity} left)")
        return len(low)
