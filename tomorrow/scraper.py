import logging

from tomorrow.client import TomorrowClient
from tomorrow.database import WeatherDBInterface
from tomorrow.models import Location

logger = logging.getLogger(__name__)


class TomorrowScraper:
    """Scrape and store weather data from Tomorrow.io."""

    def __init__(self, client: TomorrowClient, database: WeatherDBInterface) -> None:
        """Initialize the TomorrowScraper.

        Args:
            client: The Tomorrow.io API client.
            database: The weather database.
        """
        self.client = client
        self.database = database

    def scrape_forecast(self, locations: list[Location]) -> None:
        """Scrape and store forecast data for the given locations.

        Args:
            locations: The locations to scrape forecast data for.
        """
        for location in locations:
            logger.info("Scraping forecast data for %s", location)
            forecast_data = self.client.get_forecast(location)
            self.database.store_forecast(location, forecast_data)

    def scrape_history(self, locations: list[Location]) -> None:
        """Scrape and store recent history data for the given locations.

        Args:
            locations: The locations to scrape historical data for.
        """
        for location in locations:
            logger.info("Scraping history data for %s", location)
            history_data = self.client.get_history(location)
            self.database.store_history(location, history_data)

    def scrape(self) -> None:
        """Scrape and store forecast and historical weather data."""
        logger.info("Scraping forecast and historical weather data")
        locations = self.database.get_locations()
        self.scrape_forecast(locations)
        self.scrape_history(locations)
