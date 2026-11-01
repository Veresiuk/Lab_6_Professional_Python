import pytest

from shop.config import DEFAULT_MIN_STOCK, ENV_MIN_STOCK, Config
from shop.exceptions import ConfigurationError


def test_default_config_when_env_missing(monkeypatch):
    monkeypatch.delenv(ENV_MIN_STOCK, raising=False)
    assert Config.from_env().min_stock == DEFAULT_MIN_STOCK


def test_min_stock_is_read_from_environment(monkeypatch):
    monkeypatch.setenv(ENV_MIN_STOCK, "12")
    assert Config.from_env().min_stock == 12


@pytest.mark.parametrize("raw", ["abc", "1.5", ""])
def test_non_integer_min_stock_raises(monkeypatch, raw):
    monkeypatch.setenv(ENV_MIN_STOCK, raw)
    with pytest.raises(ConfigurationError, match="must be an integer"):
        Config.from_env()


def test_negative_min_stock_raises(monkeypatch):
    monkeypatch.setenv(ENV_MIN_STOCK, "-1")
    with pytest.raises(ConfigurationError, match="negative"):
        Config.from_env()
