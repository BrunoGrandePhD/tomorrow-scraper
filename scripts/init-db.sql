-- Location table to store unique locations
CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(6, 4) NOT NULL,
    longitude DECIMAL(7, 4) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (latitude, longitude)
);

-- Combined weather table for both forecast and historical data
CREATE TABLE weather (
    location_id INTEGER NOT NULL,
    time TIMESTAMP WITH TIME ZONE NOT NULL,

    is_forecast BOOLEAN NOT NULL,

    temperature REAL,
    temperature_apparent REAL,
    dew_point REAL,
    humidity REAL,
    pressure_surface_level REAL,
    wind_speed REAL,
    wind_gust REAL,
    wind_direction REAL,
    precipitation_probability REAL,
    rain_intensity REAL,
    rain_accumulation REAL,
    rain_accumulation_lwe REAL,
    snow_intensity REAL,
    snow_accumulation REAL,
    snow_accumulation_lwe REAL,
    snow_depth REAL,
    sleet_intensity REAL,
    sleet_accumulation REAL,
    sleet_accumulation_lwe REAL,
    freezing_rain_intensity REAL,
    ice_accumulation REAL,
    ice_accumulation_lwe REAL,
    cloud_base REAL,
    cloud_ceiling REAL,
    cloud_cover REAL,
    evapotranspiration REAL,
    uv_index REAL,
    uv_health_concern REAL,
    visibility REAL,
    weather_code INTEGER,

    PRIMARY KEY (location_id, time),
    FOREIGN KEY (location_id) REFERENCES location (id)
);

-- Create index for is_forecast column
CREATE INDEX idx_weather_is_forecast
ON weather (is_forecast);

-- Insert sample data into location table
INSERT INTO location (latitude, longitude)
VALUES
(25.8600, -97.4200),
(25.9000, -97.5200),
(25.9000, -97.4800),
(25.9000, -97.4400),
(25.9000, -97.4000),
(25.9200, -97.3800),
(25.9400, -97.5400),
(25.9400, -97.5200),
(25.9400, -97.4800),
(25.9400, -97.4400);
