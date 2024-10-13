import random
import zoneinfo
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pytest_postgresql import factories

from tomorrow.database import PostgresWeatherDB, get_postgres_kwargs
from tomorrow.models import Location, WeatherData, WeatherValues

TESTS_DIR = Path(__file__).parent

LOCATION = Location(25.8600, -97.4200)


postgres_kwargs = get_postgres_kwargs()
postgresql_in_docker = factories.postgresql_noproc(
    load=[TESTS_DIR / "../scripts/init-db.sql"],
    **postgres_kwargs,
)
postgresql_connection = factories.postgresql("postgresql_in_docker", dbname="test")


@pytest.fixture
def postgres_db(postgresql_connection):
    postgres_db = PostgresWeatherDB(postgresql_connection)
    yield postgres_db


def generate_weather_data(count: int) -> list[WeatherData]:
    """Generate a list of WeatherData objects for testing purposes.

    The generated data starts from the current UTC time and
    increments hourly. Temperature values are randomly generated
    between 30 and 100 degrees.

    Args:
        count: The number of WeatherData objects to generate.

    Returns:
        A list of WeatherData objects with random temperature values.
    """
    weather_data = []
    # zoneinfo is used to match datetimes from database
    start_time = datetime.now(zoneinfo.ZoneInfo(key="Etc/UTC"))
    for index in range(count):
        time = start_time + timedelta(hours=index)
        weather_vals = WeatherValues(
            temperature=random.randint(30, 100),
            temperature_apparent=random.randint(30, 100),
        )
        weather_datum = WeatherData(time, weather_vals)
        weather_data.append(weather_datum)
    return weather_data


@pytest.mark.integration
class TestPostgresStoreIntegration:
    def test_store_forecast(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_forecast(LOCATION, weather_data)
        assert postgres_db.get_count() == 3

    def test_store_forecast_update_with_new_rows(self, postgres_db):
        weather_data = generate_weather_data(5)
        postgres_db.store_forecast(LOCATION, weather_data[:3])
        assert postgres_db.get_count() == 3
        postgres_db.store_forecast(LOCATION, weather_data[3:])
        assert postgres_db.get_count() == 5

    def test_store_forecast_update_with_new_forecast(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_forecast(LOCATION, weather_data)

        # Change temperature forecast
        for weather_datum in weather_data:
            weather_datum.values.temperature += 10

        postgres_db.store_forecast(LOCATION, weather_data)
        assert postgres_db.get_count() == 3

    def test_store_forecast_update_with_history(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_forecast(LOCATION, weather_data)

        # Change temperature forecast
        for weather_datum in weather_data:
            weather_datum.values.temperature += 10

        postgres_db.store_history(LOCATION, weather_data)
        assert postgres_db.get_count() == 3

    def test_get_forecast(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_forecast(LOCATION, weather_data)
        result = postgres_db.get_forecast(LOCATION)
        assert result == weather_data

    def test_get_forecast_update_with_new_forecast(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_forecast(LOCATION, weather_data)

        # Change temperature forecast
        new_weather_data = []
        for weather_datum in weather_data:
            vals = weather_datum.values
            new_weather_vals = replace(vals, temperature=vals.temperature + 10)
            new_weather_datum = replace(weather_datum, values=new_weather_vals)
            new_weather_data.append(new_weather_datum)

        postgres_db.store_forecast(LOCATION, new_weather_data)
        result = postgres_db.get_forecast(LOCATION)
        assert result == new_weather_data

    def test_get_history(self, postgres_db):
        weather_data = generate_weather_data(3)
        postgres_db.store_history(LOCATION, weather_data)
        result = postgres_db.get_history(LOCATION)
        assert result == weather_data
