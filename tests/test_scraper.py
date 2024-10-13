from unittest.mock import create_autospec

import pytest
from requests.exceptions import HTTPError

from tests.database import InMemoryWeatherDB
from tomorrow.client import TomorrowClient, process_json
from tomorrow.models import Location
from tomorrow.scraper import TomorrowScraper

LOCATIONS = [Location(25.8600, -97.4200)]


@pytest.fixture
def mock_client():
    mock_client = create_autospec(TomorrowClient, spec_set=True)
    yield mock_client


@pytest.fixture
def test_db():
    return InMemoryWeatherDB()


@pytest.fixture
def scraper(mock_client, test_db):
    return TomorrowScraper(mock_client, test_db)


def test_scrape_forecast(mock_client, test_db, scraper, forecast_data):
    mock_client.get_forecast.return_value = process_json(forecast_data)
    assert test_db.get_count() == 0
    scraper.scrape_forecast(LOCATIONS)
    assert test_db.get_count() == 120  # Manually obtained from forecast.json


def test_scrape_history(mock_client, test_db, scraper, history_data):
    mock_client.get_history.return_value = process_json(history_data)
    assert test_db.get_count() == 0
    scraper.scrape_history(LOCATIONS)
    assert test_db.get_count() == 24  # Manually obtained from history.json


def test_scrape_and_store_forecast_empty(mock_client, test_db, scraper):
    mock_client.get_forecast.return_value = process_json({})
    assert test_db.get_count() == 0
    scraper.scrape_forecast(LOCATIONS)
    assert test_db.get_count() == 0


def test_scrape_and_store_history_empty(mock_client, test_db, scraper):
    mock_client.get_history.return_value = process_json({})
    assert test_db.get_count() == 0
    scraper.scrape_history(LOCATIONS)
    assert test_db.get_count() == 0


def test_scrape_and_store_forecast_http_error(mock_client, test_db, scraper):
    mock_client.get_forecast.side_effect = HTTPError("Test error")
    assert test_db.get_count() == 0
    with pytest.raises(HTTPError):
        scraper.scrape_forecast(LOCATIONS)


def test_scrape_and_store_history_http_error(mock_client, test_db, scraper):
    mock_client.get_history.side_effect = HTTPError("Test error")
    assert test_db.get_count() == 0
    with pytest.raises(HTTPError):
        scraper.scrape_history(LOCATIONS)
