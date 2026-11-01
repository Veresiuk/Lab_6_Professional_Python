"""Pipeline: import -> processing -> export."""
from __future__ import annotations

from pathlib import Path

from shop.config import Config
from shop.exporters import export_products_to_json
from shop.importers import import_products_from_csv
from shop.repositories import InMemoryProductRepository
from shop.services import Catalog


def run_pipeline(csv_path: Path, json_path: Path, config: Config | None = None) -> dict[str, float]:
    """Import products, compute statistics and export them to JSON."""
    catalog = Catalog(InMemoryProductRepository(), config)
    for product in import_products_from_csv(csv_path):
        catalog.add_product(product)
    export_products_to_json(catalog.all_products(), json_path)
    best = catalog.most_expensive()
    return {
        "total_stock_value": catalog.total_stock_value(),
        "low_stock_count": len(catalog.low_stock_products()),
        "most_expensive_price": best.price if best else 0.0,
    }
