import logging
import os
from abc import ABC, abstractmethod

import psycopg
from psycopg.rows import dict_row

from tomorrow.models import Location, WeatherData, WeatherValues

logger = logging.getLogger(__name__)


class WeatherDBInterface(ABC):
    """An interface for storing weather data in a database."""

    @abstractmethod
    def store_forecast(
        self,
        location: Location,
        forecast_data: list[WeatherData],
    ) -> None:
        """Store forecast data for a given location.

        Args:
            location: The location to store the forecast data for.
            forecast_data: The forecast data to store.
        """
        ...

    @abstractmethod
    def store_history(
        self,
        location: Location,
        history_data: list[WeatherData],
    ) -> None:
        """Store historical data for a given location.

        Args:
            location: The location to store the historical data for.
            history_data: The historical data to store.
        """
        ...

    @abstractmethod
    def get_locations(self, active_only: bool = True) -> list[Location]:
        """Get all locations.

        Args:
            active_only: Whether to only get active locations.

        Returns:
            A list of locations.
        """
        ...

    @abstractmethod
    def get_forecast(self, location: Location) -> list[WeatherData]:
        """Get forecast data for a given location.

        Args:
            location: The location to get the forecast data for.

        Returns:
            A list of forecast weather data.
        """
        ...

    @abstractmethod
    def get_history(self, location: Location) -> list[WeatherData]:
        """Get historical data for a given location.

        Args:
            location: The location to get the historical data for.

        Returns:
            A list of historical weather data.
        """
        ...

    @abstractmethod
    def get_count(self) -> int:
        """Get the total number of weather entries.

        Returns:
            The total number of weather entries.
        """
        ...


def get_postgres_kwargs() -> dict:
    """Get Postgres connection info from environment variables."""
    kwargs = {
        "host": os.getenv("PGHOST"),
        "port": os.getenv("PGPORT"),
        "user": os.getenv("PGUSER"),
        "password": os.getenv("PGPASSWORD"),
    }
    if not all(kwargs.values()):
        msg = f"Postgres environment variables not set (current env: {os.environ})"
        raise RuntimeError(msg)
    return kwargs


class PostgresWeatherDB(WeatherDBInterface):
    """A Postgres implementation of the WeatherDBInterface."""

    def __init__(self, connection: psycopg.Connection):
        """Initialize the PostgresWeatherDB.

        Args:
            connection: A psycopg connection object.
        """
        self.conn = connection

    def store_forecast(self, location: Location, forecast_data: list[WeatherData]):
        """Store forecast data for a given location.

        Args:
            location: The location to store the forecast data for.
            forecast_data: The forecast data to store.
        """
        logger.info("Storing forecast data for %s", location)
        self._store_data(location, forecast_data, is_forecast=True)

    def store_history(self, location: Location, history_data: list[WeatherData]):
        """Store historical data for a given location.

        Args:
            location: The location to store the historical data for.
            history_data: The historical data to store.
        """
        logger.info("Storing historical data for %s", location)
        self._store_data(location, history_data, is_forecast=False)

    def _store_data(
        self, location: Location, data: list[WeatherData], is_forecast: bool
    ):
        """Store data for a given location.

        Args:
            location: The location to store the data for.
            data: The weather data to store.
            is_forecast: Whether the data is forecast data.
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            # Get location ID or raise error if not found
            cur.execute(
                """
                SELECT id FROM location
                WHERE latitude = %s AND longitude = %s
                """,
                (location.latitude, location.longitude),
            )
            result = cur.fetchone()
            if result is None:
                raise ValueError(f"Location not found: {location}")
            location_id = result["id"]

            # Prepare data for batch insert
            values = [
                (
                    location_id,
                    d.time,
                    is_forecast,
                    d.values.temperature,
                    d.values.temperature_apparent,
                    d.values.dew_point,
                    d.values.humidity,
                    d.values.pressure_surface_level,
                    d.values.wind_speed,
                    d.values.wind_gust,
                    d.values.wind_direction,
                    d.values.precipitation_probability,
                    d.values.rain_intensity,
                    d.values.rain_accumulation,
                    d.values.rain_accumulation_lwe,
                    d.values.snow_intensity,
                    d.values.snow_accumulation,
                    d.values.snow_accumulation_lwe,
                    d.values.snow_depth,
                    d.values.sleet_intensity,
                    d.values.sleet_accumulation,
                    d.values.sleet_accumulation_lwe,
                    d.values.freezing_rain_intensity,
                    d.values.ice_accumulation,
                    d.values.ice_accumulation_lwe,
                    d.values.cloud_base,
                    d.values.cloud_ceiling,
                    d.values.cloud_cover,
                    d.values.evapotranspiration,
                    d.values.uv_index,
                    d.values.uv_health_concern,
                    d.values.visibility,
                )
                for d in data
            ]

            # Perform batch insert
            cur.executemany(
                """
                INSERT INTO weather (
                    location_id, time, is_forecast, temperature, temperature_apparent,
                    dew_point, humidity, pressure_surface_level, wind_speed, wind_gust,
                    wind_direction, precipitation_probability, rain_intensity,
                    rain_accumulation, rain_accumulation_lwe, snow_intensity,
                    snow_accumulation, snow_accumulation_lwe, snow_depth, sleet_intensity,
                    sleet_accumulation, sleet_accumulation_lwe, freezing_rain_intensity,
                    ice_accumulation, ice_accumulation_lwe, cloud_base, cloud_ceiling,
                    cloud_cover, evapotranspiration, uv_index, uv_health_concern, visibility
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (location_id, time)
                DO UPDATE SET
                    is_forecast = EXCLUDED.is_forecast,
                    temperature = EXCLUDED.temperature,
                    temperature_apparent = EXCLUDED.temperature_apparent,
                    dew_point = EXCLUDED.dew_point,
                    humidity = EXCLUDED.humidity,
                    pressure_surface_level = EXCLUDED.pressure_surface_level,
                    wind_speed = EXCLUDED.wind_speed,
                    wind_gust = EXCLUDED.wind_gust,
                    wind_direction = EXCLUDED.wind_direction,
                    precipitation_probability = EXCLUDED.precipitation_probability,
                    rain_intensity = EXCLUDED.rain_intensity,
                    rain_accumulation = EXCLUDED.rain_accumulation,
                    rain_accumulation_lwe = EXCLUDED.rain_accumulation_lwe,
                    snow_intensity = EXCLUDED.snow_intensity,
                    snow_accumulation = EXCLUDED.snow_accumulation,
                    snow_accumulation_lwe = EXCLUDED.snow_accumulation_lwe,
                    snow_depth = EXCLUDED.snow_depth,
                    sleet_intensity = EXCLUDED.sleet_intensity,
                    sleet_accumulation = EXCLUDED.sleet_accumulation,
                    sleet_accumulation_lwe = EXCLUDED.sleet_accumulation_lwe,
                    freezing_rain_intensity = EXCLUDED.freezing_rain_intensity,
                    ice_accumulation = EXCLUDED.ice_accumulation,
                    ice_accumulation_lwe = EXCLUDED.ice_accumulation_lwe,
                    cloud_base = EXCLUDED.cloud_base,
                    cloud_ceiling = EXCLUDED.cloud_ceiling,
                    cloud_cover = EXCLUDED.cloud_cover,
                    evapotranspiration = EXCLUDED.evapotranspiration,
                    uv_index = EXCLUDED.uv_index,
                    uv_health_concern = EXCLUDED.uv_health_concern,
                    visibility = EXCLUDED.visibility
            """,
                values,
            )

        self.conn.commit()

    def get_locations(self, active_only: bool = True) -> list[Location]:
        """Get all locations.

        Args:
            active_only: Whether to only get active locations.

        Returns:
            A list of locations.
        """
        logger.info("Getting locations")
        with self.conn.cursor() as cur:
            filter_clause = "WHERE is_active = TRUE" if active_only else ""
            query = f"""
                SELECT DISTINCT latitude, longitude
                FROM location
                {filter_clause}
                ORDER BY latitude, longitude
            """
            cur.execute(query)
            rows = cur.fetchall()

        return [Location(*row) for row in rows]

    def get_forecast(self, location: Location) -> list[WeatherData]:
        """Get forecast data for a given location.

        Args:
            location: The location to get the forecast data for.

        Returns:
            A list of forecast weather data.
        """
        logger.info("Getting forecast data for %s", location)
        return self._get_data(location, is_forecast=True)

    def get_history(self, location: Location) -> list[WeatherData]:
        """Get historical data for a given location.

        Args:
            location: The location to get the historical data for.

        Returns:
            A list of historical weather data.
        """
        logger.info("Getting historical data for %s", location)
        return self._get_data(location, is_forecast=False)

    def _get_data(self, location: Location, is_forecast: bool) -> list[WeatherData]:
        """Get weather data for a given location.

        Args:
            location: The location to get the data for.
            is_forecast: Whether to get forecast data.

        Returns:
            A list of weather data.
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT w.* FROM weather w
                JOIN location l ON w.location_id = l.id
                WHERE l.latitude = %s
                    AND l.longitude = %s
                    AND w.is_forecast = %s
                ORDER BY w.time
                """,
                (location.latitude, location.longitude, is_forecast),
            )
            rows = cur.fetchall()

        return [
            WeatherData(time=row["time"], values=WeatherValues.from_dict(row))
            for row in rows
        ]

    def get_count(self) -> int:
        """Get the total number of weather entries.

        Returns:
            The total number of weather entries.
        """
        logger.info("Counting number of weather entries")
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM weather")
            count = cursor.fetchone()
            if count is None:
                raise ValueError("No weather entries found")
        return count[0]
