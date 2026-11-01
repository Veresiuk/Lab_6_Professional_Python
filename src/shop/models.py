"""Domain model: Product."""
from __future__ import annotations

from dataclasses import dataclass

from shop.exceptions import ProductValidationError


@dataclass(slots=True)
class Product:
    """A product in the online shop catalog."""

    sku: str
    name: str
    category: str
    price: float
    quantity: int

    def __post_init__(self) -> None:
        self.sku = self._require_text(self.sku, "sku")
        self.name = self._require_text(self.name, "name")
        self.category = self._require_text(self.category, "category")
        if isinstance(self.price, bool) or not isinstance(self.price, (int, float)):
            raise ProductValidationError("Price must be a number")
        if self.price < 0:
            raise ProductValidationError("Price cannot be negative")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ProductValidationError("Quantity must be an integer")
        if self.quantity < 0:
            raise ProductValidationError("Quantity cannot be negative")

    @staticmethod
    def _require_text(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ProductValidationError(f"Field '{field}' must not be empty")
        return value.strip()

    @property
    def stock_value(self) -> float:
        """Total value of the product stock."""
        return self.price * self.quantity

    def to_dict(self) -> dict[str, object]:
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
        }
