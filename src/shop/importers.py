"""CSV import of products."""
from __future__ import annotations

import csv
from pathlib import Path

from shop.exceptions import MalformedRecordError, ProductValidationError
from shop.models import Product

REQUIRED_COLUMNS = ("sku", "name", "category", "price", "quantity")


def import_products_from_csv(path: Path) -> list[Product]:
    """Read products from a CSV file with a header row."""
    products: list[Product] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise MalformedRecordError(f"Missing columns: {', '.join(missing)}")
        for line_no, row in enumerate(reader, start=2):
            try:
                products.append(
                    Product(
                        sku=row["sku"],
                        name=row["name"],
                        category=row["category"],
                        price=float(row["price"]),
                        quantity=int(row["quantity"]),
                    )
                )
            except (TypeError, ValueError, ProductValidationError) as exc:
                raise MalformedRecordError(f"Line {line_no}: {exc}") from exc
    return products
