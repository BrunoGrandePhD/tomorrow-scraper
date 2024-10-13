from datetime import datetime

from tomorrow.database import WeatherDBInterface
from tomorrow.models import Location, WeatherData


class InMemoryWeatherDB(WeatherDBInterface):
    """An in-memory implementation of the WeatherDBInterface.

    Note that some values are hard-coded for testing purposes.
    """

    def __init__(self) -> None:
        """Initialize the in-memory database."""
        self.data: dict[tuple[str, datetime], tuple[WeatherData, bool]] = {}

    def store_forecast(
        self,
        location: Location,
        forecast_data: list[WeatherData],
    ) -> None:
        """Store forecast data.

        Args:
            location: The location to store the forecast data for.
            forecast_data: The forecast data to store.
        """
        self._store_data(location, forecast_data, True)

    def store_history(
        self,
        location: Location,
        history_data: list[WeatherData],
    ) -> None:
        """Store historical data.

        Args:
            location: The location to store the historical data for.
            history_data: The historical data to store.
        """
        self._store_data(location, history_data, False)

    def _store_data(
        self,
        location: Location,
        data: list[WeatherData],
        is_forecast: bool,
    ) -> None:
        """Store weather data.

        Args:
            location: The location to store the data for.
            data: The weather data to store.
            is_forecast: Whether the data is forecast data.
        """
        for datum in data:
            self.data[(location.to_string(), datum.time)] = (datum, is_forecast)

    def get_locations(self, active_only: bool = True) -> list[Location]:
        """Get all locations in the database.

        Args:
            active_only: Whether to only return active locations.

        Returns:
            A list of locations.
        """
        locations = [
            Location(25.8600, -97.4200),
            Location(25.9000, -97.5200),
            Location(25.9000, -97.4800),
        ]
        return locations

    def get_forecast(self, location: Location) -> list[WeatherData]:
        """Get forecast data for a given location.

        Args:
            location: The location to get the forecast data for.

        Returns:
            A list of forecast weather data.
        """
        return [
            datum
            for (loc, _), (datum, is_forecast) in self.data.items()
            if loc == location.to_string() and is_forecast
        ]

    def get_history(self, location: Location) -> list[WeatherData]:
        """Get historical data for a given location.

        Args:
            location: The location to get the historical data for.

        Returns:
            A list of historical weather data.
        """
        return [
            datum
            for (loc, _), (datum, is_forecast) in self.data.items()
            if loc == location.to_string() and not is_forecast
        ]

    def get_count(self) -> int:
        """Get the total number of weather entries.

        Returns:
            The total number of weather entries.
        """
        return len(self.data)
