import pytest

from shop.exceptions import ProductValidationError
from shop.models import Product


def test_product_creation_strips_text_fields():
    product = Product("  A-1 ", " Laptop ", " electronics ", 100, 2)
    assert (product.sku, product.name, product.category) == ("A-1", "Laptop", "electronics")


def test_stock_value_uses_approx_for_floats():
    product = Product("X", "Pen", "stationery", 0.1, 3)
    assert product.stock_value == pytest.approx(0.3)


@pytest.mark.parametrize(
    "price, quantity",
    [(0, 0), (0.0, 1), (1, 0), (10**6, 10**6)],
    ids=["zero-zero", "zero-price", "zero-quantity", "large-values"],
)
def test_boundary_price_and_quantity_are_accepted(price, quantity):
    product = Product("X", "Item", "misc", price, quantity)
    assert product.stock_value >= 0


@pytest.mark.parametrize(
    "price, quantity, message",
    [
        (-0.01, 1, "Price cannot be negative"),
        (10, -1, "Quantity cannot be negative"),
        ("10", 1, "Price must be a number"),
        (True, 1, "Price must be a number"),
        (10, 1.5, "Quantity must be an integer"),
        (10, True, "Quantity must be an integer"),
    ],
)
def test_invalid_price_or_quantity_raises_validation_error(price, quantity, message):
    with pytest.raises(ProductValidationError, match=message):
        Product("X", "Item", "misc", price, quantity)


@pytest.mark.parametrize("field", ["sku", "name", "category"])
def test_empty_text_field_is_rejected(field):
    data = {"sku": "X", "name": "Item", "category": "misc", "price": 1, "quantity": 1}
    data[field] = "   "
    with pytest.raises(ProductValidationError) as exc_info:
        Product(**data)
    assert field in str(exc_info.value)


def test_custom_exception_is_also_value_error():
    with pytest.raises(ValueError):
        Product("X", "Item", "misc", -1, 1)


def test_to_dict_contains_all_fields(laptop):
    assert laptop.to_dict() == {
        "sku": "A-1",
        "name": "Laptop",
        "category": "electronics",
        "price": 25000.0,
        "quantity": 3,
    }
