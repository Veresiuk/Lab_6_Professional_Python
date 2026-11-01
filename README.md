# Shop Project

Лабораторна робота №6 «Автоматизоване тестування Python-програм», варіант №3 — «Інтернет-магазин».

## Installation
    python -m venv .venv
    .venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
    python -m pip install -e ".[dev]"

## Run application
    python -m shop.main products.csv output.json

## Run tests + coverage
    pytest -v --cov=shop --cov-branch --cov-report=term-missing --cov-report=html

Лише unit: `pytest -m "not integration"`; лише integration: `pytest -m integration`.
HTML-звіт coverage: `htmlcov/index.html`.
