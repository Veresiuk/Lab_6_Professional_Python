"""JSON export of products."""
from __future__ import annotations

import json
from pathlib import Path

from shop.models import Product


def export_products_to_json(products: list[Product], path: Path) -> int:
    """Write products to a JSON file; returns the number of exported items."""
    data = [p.to_dict() for p in products]
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data)
