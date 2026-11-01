"""Application configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

from shop.exceptions import ConfigurationError

ENV_MIN_STOCK = "SHOP_MIN_STOCK"
DEFAULT_MIN_STOCK = 5


@dataclass(frozen=True, slots=True)
class Config:
    min_stock: int = DEFAULT_MIN_STOCK

    @classmethod
    def from_env(cls) -> "Config":
        """Read configuration from environment variables."""
        raw = os.environ.get(ENV_MIN_STOCK)
        if raw is None:
            return cls()
        try:
            value = int(raw)
        except ValueError as exc:
            raise ConfigurationError(f"{ENV_MIN_STOCK} must be an integer, got {raw!r}") from exc
        if value < 0:
            raise ConfigurationError(f"{ENV_MIN_STOCK} cannot be negative")
        return cls(min_stock=value)
