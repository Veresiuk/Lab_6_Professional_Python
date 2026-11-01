"""Async external price provider (simulated network call)."""
from __future__ import annotations

import asyncio

from shop.exceptions import ExternalServiceError
from shop.protocols import PriceProvider


class FakeRemotePriceProvider:
    """Stand-in for a remote HTTP service with a fixed price list."""

    def __init__(self, prices: dict[str, float], delay: float = 0.0) -> None:
        self._prices = prices
        self._delay = delay

    async def fetch_price(self, sku: str) -> float:
        await asyncio.sleep(self._delay)
        try:
            return self._prices[sku]
        except KeyError as exc:
            raise ExternalServiceError(f"No price for {sku}") from exc


async def refresh_prices(products: list, provider: PriceProvider) -> int:
    """Update product prices from an external provider; returns updated count."""
    updated = 0
    for product in products:
        new_price = await provider.fetch_price(product.sku)
        if new_price != product.price:
            product.price = new_price
            updated += 1
    return updated
