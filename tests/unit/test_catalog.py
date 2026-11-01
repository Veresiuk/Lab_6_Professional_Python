import pytest

from shop.exceptions import DuplicateProductError, ProductNotFoundError
from shop.models import Product


def test_add_product_makes_it_findable(empty_catalog, laptop):
    empty_catalog.add_product(laptop)
    assert empty_catalog.find_product("A-1") is laptop


def test_duplicate_sku_is_rejected(catalog, laptop):
    with pytest.raises(DuplicateProductError):
        catalog.add_product(Product("A-1", "Other", "misc", 1, 1))


def test_find_unknown_product_raises_not_found(catalog):
    with pytest.raises(ProductNotFoundError, match="Z-9"):
        catalog.find_product("Z-9")


def test_search_by_name_is_case_insensitive(catalog):
    names = [p.name for p in catalog.search_by_name("  MOU ")]
    assert names == ["Mouse"]


def test_filter_by_category(catalog):
    skus = {p.sku for p in catalog.filter_by_category("Electronics")}
    assert skus == {"A-1", "B-2"}


def test_filter_by_unknown_category_returns_empty_list(catalog):
    assert catalog.filter_by_category("food") == []


def test_total_stock_value(catalog):
    assert catalog.total_stock_value() == pytest.approx(25000 * 3 + 500 * 20 + 40.5 * 100)


def test_most_expensive_product(catalog):
    assert catalog.most_expensive().sku == "A-1"


def test_empty_catalog_has_zero_value_and_no_best_product(empty_catalog):
    assert empty_catalog.total_stock_value() == 0
    assert empty_catalog.most_expensive() is None
    assert empty_catalog.all_products() == []


def test_low_stock_uses_min_stock_from_config(catalog):
    assert [p.sku for p in catalog.low_stock_products()] == ["A-1"]


@pytest.mark.parametrize(
    "quantity, expected_low",
    [(4, True), (5, False), (6, False)],
    ids=["below-threshold", "at-threshold", "above-threshold"],
)
def test_low_stock_boundary(empty_catalog, quantity, expected_low):
    empty_catalog.add_product(Product("X", "Item", "misc", 1, quantity))
    assert bool(empty_catalog.low_stock_products()) is expected_low
