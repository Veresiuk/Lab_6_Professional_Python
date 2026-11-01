import json

import pytest

from shop.exceptions import MalformedRecordError
from shop.exporters import export_products_to_json
from shop.importers import import_products_from_csv


def test_csv_import_reads_all_products(csv_file):
    products = import_products_from_csv(csv_file)
    assert [p.sku for p in products] == ["A-1", "B-2", "C-3"]
    assert products[2].price == pytest.approx(40.5)


def test_csv_import_missing_column(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("sku,name\nA,B\n", encoding="utf-8")
    with pytest.raises(MalformedRecordError, match="Missing columns"):
        import_products_from_csv(path)


@pytest.mark.parametrize(
    "row",
    ["A-1,Laptop,electronics,abc,3", "A-1,Laptop,electronics,10,x", "A-1,Laptop,electronics,-5,3", ",Laptop,electronics,10,3"],
    ids=["bad-price", "bad-quantity", "negative-price", "empty-sku"],
)
def test_malformed_record_raises_with_line_number(tmp_path, row):
    path = tmp_path / "bad.csv"
    path.write_text(f"sku,name,category,price,quantity\n{row}\n", encoding="utf-8")
    with pytest.raises(MalformedRecordError, match="Line 2"):
        import_products_from_csv(path)


def test_json_export_writes_valid_file(tmp_path, sample_products):
    target = tmp_path / "out.json"
    count = export_products_to_json(sample_products, target)
    data = json.loads(target.read_text(encoding="utf-8"))
    assert count == 3
    assert data[0]["name"] == "Laptop"


def test_json_export_of_empty_list(tmp_path):
    target = tmp_path / "empty.json"
    assert export_products_to_json([], target) == 0
    assert json.loads(target.read_text(encoding="utf-8")) == []
