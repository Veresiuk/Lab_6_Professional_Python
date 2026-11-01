import json

import pytest

from shop.config import Config
from shop.exceptions import DuplicateProductError, MalformedRecordError
from shop.main import main
from shop.pipeline import run_pipeline
from shop.providers import FakeRemotePriceProvider, refresh_prices
from shop.repositories import InMemoryProductRepository
from shop.importers import import_products_from_csv
from shop.exporters import export_products_to_json

pytestmark = pytest.mark.integration


def test_import_processing_export_pipeline(csv_file, tmp_path):
    out = tmp_path / "result.json"
    stats = run_pipeline(csv_file, out, Config(min_stock=5))
    exported = json.loads(out.read_text(encoding="utf-8"))
    assert [p["sku"] for p in exported] == ["A-1", "B-2", "C-3"]
    assert stats["total_stock_value"] == pytest.approx(89050.0)
    assert stats["low_stock_count"] == 1
    assert stats["most_expensive_price"] == 25000


def test_pipeline_fails_on_malformed_csv_and_writes_nothing(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("sku,name,category,price,quantity\nA,B,C,x,1\n", encoding="utf-8")
    out = tmp_path / "out.json"
    with pytest.raises(MalformedRecordError):
        run_pipeline(bad, out)
    assert not out.exists()


def test_pipeline_rejects_duplicate_skus(tmp_path):
    path = tmp_path / "dup.csv"
    path.write_text(
        "sku,name,category,price,quantity\nA,One,c,1,1\nA,Two,c,2,2\n", encoding="utf-8"
    )
    with pytest.raises(DuplicateProductError):
        run_pipeline(path, tmp_path / "o.json")


def test_main_uses_min_stock_from_environment(csv_file, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SHOP_MIN_STOCK", "50")
    out = tmp_path / "main.json"
    assert main([str(csv_file), str(out)]) == 0
    printed = capsys.readouterr().out
    assert "low_stock_count: 2.00" in printed
    assert out.exists()


def test_main_prints_usage_for_wrong_arguments(capsys):
    assert main([]) == 2
    assert "Usage" in capsys.readouterr().out


def test_empty_csv_produces_empty_export(tmp_path):
    src = tmp_path / "empty.csv"
    src.write_text("sku,name,category,price,quantity\n", encoding="utf-8")
    out = tmp_path / "empty.json"
    stats = run_pipeline(src, out)
    assert json.loads(out.read_text(encoding="utf-8")) == []
    assert stats == {"total_stock_value": 0, "low_stock_count": 0, "most_expensive_price": 0.0}


async def test_async_price_refresh_then_export(csv_file, tmp_path):
    products = import_products_from_csv(csv_file)
    provider = FakeRemotePriceProvider({"A-1": 24000.0, "B-2": 500.0, "C-3": 50.0})
    assert await refresh_prices(products, provider) == 2
    out = tmp_path / "prices.json"
    export_products_to_json(products, out)
    data = {p["sku"]: p["price"] for p in json.loads(out.read_text(encoding="utf-8"))}
    assert data == {"A-1": 24000.0, "B-2": 500.0, "C-3": 50.0}
