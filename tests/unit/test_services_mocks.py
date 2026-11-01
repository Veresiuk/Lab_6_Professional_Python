from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from shop.exceptions import ExternalServiceError, ProductNotFoundError
from shop.protocols import DiscountProvider, Notifier
from shop.providers import FakeRemotePriceProvider, refresh_prices
from shop.services import Catalog, PricingService, StockMonitor


# ---- ProductRepository mocked ------------------------------------------------
def test_catalog_find_uses_repository_get(laptop):
    repo = Mock()
    repo.get.return_value = laptop
    assert Catalog(repo).find_product("A-1") is laptop
    repo.get.assert_called_once_with("A-1")


def test_catalog_raises_when_repository_returns_none():
    repo = Mock()
    repo.get.return_value = None
    with pytest.raises(ProductNotFoundError):
        Catalog(repo).find_product("nope")


def test_add_product_delegates_to_repository(laptop):
    repo = Mock()
    Catalog(repo).add_product(laptop)
    repo.add.assert_called_once_with(laptop)


# ---- Pricing with return_value / side_effect --------------------------------
def test_discount_applied_from_provider_return_value(laptop):
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.return_value = 10
    assert PricingService(provider).discounted_price(laptop) == pytest.approx(22500.0)
    provider.get_discount.assert_called_once_with("electronics")


def test_provider_failure_is_wrapped_via_side_effect(laptop):
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.side_effect = ConnectionError("timeout")
    with pytest.raises(ExternalServiceError, match="failed") as exc_info:
        PricingService(provider).discounted_price(laptop)
    assert isinstance(exc_info.value.__cause__, ConnectionError)


@pytest.mark.parametrize("bad_discount", [-1, 100.1, 500])
def test_invalid_discount_from_provider_rejected(laptop, bad_discount):
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.return_value = bad_discount
    with pytest.raises(ExternalServiceError, match="Invalid discount"):
        PricingService(provider).discounted_price(laptop)


@pytest.mark.parametrize("percent, expected", [(0, 25000.0), (100, 0.0)])
def test_discount_boundaries(laptop, percent, expected):
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.return_value = percent
    assert PricingService(provider).discounted_price(laptop) == pytest.approx(expected)


# ---- Notifier: interaction testing ------------------------------------------
def test_stock_monitor_notifies_for_each_low_stock_product(catalog):
    notifier = Mock(spec=Notifier)
    assert StockMonitor(catalog, notifier).check() == 1
    notifier.notify.assert_called_once_with("Low stock: A-1 (3 left)")


def test_stock_monitor_does_not_notify_when_stock_is_fine(empty_catalog):
    notifier = Mock(spec=Notifier)
    assert StockMonitor(empty_catalog, notifier).check() == 0
    notifier.notify.assert_not_called()


def test_notifier_failure_propagates(catalog):
    notifier = Mock(spec=Notifier)
    notifier.notify.side_effect = RuntimeError("smtp down")
    with pytest.raises(RuntimeError, match="smtp down"):
        StockMonitor(catalog, notifier).check()
    assert notifier.notify.call_count == 1


# ---- Async dependency with AsyncMock ----------------------------------------
async def test_refresh_prices_with_async_mock(sample_products):
    provider = AsyncMock()
    provider.fetch_price.side_effect = [26000.0, 500.0, 45.0]
    updated = await refresh_prices(sample_products, provider)
    assert updated == 2
    assert sample_products[0].price == 26000.0
    assert provider.fetch_price.await_count == 3
    provider.fetch_price.assert_any_await("A-1")


async def test_refresh_prices_propagates_provider_failure(laptop):
    provider = AsyncMock()
    provider.fetch_price.side_effect = ExternalServiceError("down")
    with pytest.raises(ExternalServiceError):
        await refresh_prices([laptop], provider)


async def test_fake_remote_provider_returns_price():
    provider = FakeRemotePriceProvider({"A-1": 99.0})
    assert await provider.fetch_price("A-1") == 99.0


async def test_fake_remote_provider_unknown_sku():
    with pytest.raises(ExternalServiceError, match="No price"):
        await FakeRemotePriceProvider({}).fetch_price("A-1")


def test_magicmock_supports_context_protocol_example():
    magic = MagicMock()
    magic.__len__.return_value = 3
    assert len(magic) == 3
