import json
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent


@pytest.fixture
def history_data():
    with (TESTS_DIR / "data" / "history.json").open("r") as f:
        yield json.load(f)


@pytest.fixture
def forecast_data():
    with (TESTS_DIR / "data" / "forecast.json").open("r") as f:
        yield json.load(f)
