import os

import pytest
import requests

from tomorrow.client import TomorrowClient
from tomorrow.models import Location

LOCATION = Location(25.8600, -97.4200)


@pytest.fixture
def client():
    api_key = os.getenv("TOMORROW_API_KEY")
    if not api_key:
        pytest.skip("TOMORROW_API_KEY not set in environment")
    return TomorrowClient(api_key)


@pytest.mark.integration
class TestTomorrowClientIntegration:
    def test_get_forecast(self, client):
        response = client.get_forecast(LOCATION)
        assert len(response) > 0

    def test_get_history(self, client):
        response = client.get_history(LOCATION)
        assert len(response) > 0

    def test_invalid_api_key(self):
        invalid_client = TomorrowClient("invalid_key")
        with pytest.raises(requests.exceptions.HTTPError):
            invalid_client.get_forecast(LOCATION)
