import time
from dataclasses import dataclass
from typing import Any

import requests

from tomorrow.models import Location, WeatherData


def process_json(data: dict[str, Any]) -> list[WeatherData]:
    """Process JSON data into WeatherData objects.

    Args:
        data: The Tomorrow.io API JSON data to process.

    Returns:
        A list of WeatherData objects.
    """
    timelines = data.get("timelines", {})
    hourly = timelines.get("hourly", [])
    weather_data = []
    for entry in hourly:
        weather_datum = WeatherData.schema().load(entry)
        weather_data.append(weather_datum)
    return weather_data


@dataclass
class TomorrowClient:
    """A client for the Tomorrow.io API.

    Attributes:
        api_key: The Tomorrow.io API key to use for requests.
        base_url: The base URL for the Tomorrow.io API.
        request_interval: The interval between requests to avoid rate
            limiting.
    """

    api_key: str
    base_url: str = "https://api.tomorrow.io/v4"
    request_interval: float = 0.5

    def __post_init__(self) -> None:
        """Post-initialize the client."""
        self._last_request_time = 0.0

    def get(self, url: str, params: dict) -> dict:
        """Make an authenticated GET request.

        Implements rate limiting to ensure requests are not sent more
        often than once per `request_interval` seconds.

        Args:
            url: The URL to request.
            params: The query parameters to include in the request.

        Returns:
            The JSON response from the request.
        """
        # Implement rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self.request_interval:
            time.sleep(self.request_interval - time_since_last_request)

        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Update the last request time
        self._last_request_time = time.time()

        return response.json()

    def get_forecast(
        self,
        location: Location,
        timesteps: str = "hourly",
    ) -> list[WeatherData]:
        """Get a forecast for a given location (defaults to hourly).

        Args:
            location: The location to get the forecast for.
            timesteps: The timesteps to get the forecast for. Defaults to
                hourly.

        Returns:
            A list of WeatherData objects.
        """
        url = f"{self.base_url}/weather/forecast"
        params = {
            "location": location.to_string(),
            "timesteps": timesteps,
            "apikey": self.api_key,
        }

        forecast_json = self.get(url, params)
        return process_json(forecast_json)

    def get_history(
        self,
        location: Location,
        timesteps: str = "hourly",
    ) -> list[WeatherData]:
        """Get recent history for a given location.

        Args:
            location: The location to get the history for.
            timesteps: The timesteps to get the history for. Defaults to
                hourly.

        Returns:
            A list of WeatherData objects.
        """
        url = f"{self.base_url}/weather/history/recent"
        params = {
            "location": location.to_string(),
            "timesteps": timesteps,
            "apikey": self.api_key,
        }

        history_json = self.get(url, params)
        return process_json(history_json)
