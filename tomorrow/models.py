from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, config, dataclass_json
from marshmallow import fields


@dataclass_json()
@dataclass
class Location(DataClassJsonMixin):
    """A location with latitude and longitude.

    Attributes:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """

    latitude: float
    longitude: float

    @classmethod
    def from_string(cls, value: str) -> "Location":
        """Create a Location from a string.

        Args:
            value: The string to parse. It must have the Tomorrow.io
                API format (i.e., "latitude,longitude").

        Returns:
            A Location object.
        """
        latitude, longitude = value.split(",")
        return cls(float(latitude), float(longitude))

    def to_string(self) -> str:
        """Convert the Location to a string.

        Returns:
            A string in the Tomorrow.io API format
            (i.e., "latitude,longitude").
        """
        return f"{self.latitude},{self.longitude}"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class WeatherValues(DataClassJsonMixin):
    """A set of weather values.

    Please refer to the Tomorrow.io API documentation for
    descriptions of the fields.
    """

    temperature: Optional[float] = None
    temperature_apparent: Optional[float] = None
    dew_point: Optional[float] = None
    humidity: Optional[float] = None
    pressure_surface_level: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_gust: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation_probability: Optional[float] = None
    rain_intensity: Optional[float] = None
    rain_accumulation: Optional[float] = None
    rain_accumulation_lwe: Optional[float] = None
    snow_intensity: Optional[float] = None
    snow_accumulation: Optional[float] = None
    snow_accumulation_lwe: Optional[float] = None
    snow_depth: Optional[float] = None
    sleet_intensity: Optional[float] = None
    sleet_accumulation: Optional[float] = None
    sleet_accumulation_lwe: Optional[float] = None
    freezing_rain_intensity: Optional[float] = None
    ice_accumulation: Optional[float] = None
    ice_accumulation_lwe: Optional[float] = None
    cloud_base: Optional[float] = None
    cloud_ceiling: Optional[float] = None
    cloud_cover: Optional[float] = None
    evapotranspiration: Optional[float] = None
    uv_index: Optional[float] = None
    uv_health_concern: Optional[float] = None
    visibility: Optional[float] = None
    weather_code: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class WeatherData(DataClassJsonMixin):
    """Weather data for a given time."""

    time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    values: WeatherValues
