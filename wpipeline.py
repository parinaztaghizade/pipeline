#Extract

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 59.3294,
    "longitude": 18.0687,
    "start_date": "2013-01-01",
    "end_date": "2023-11-30",
    "hourly": ["temperature_2m", "rain", "snowfall", "wind_speed_10m"]
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_rain = hourly.Variables(1).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s"),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["rain"] = hourly_rain
hourly_data["snowfall"] = hourly_snowfall
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

hourly_dataframe = pd.DataFrame(data=hourly_data)


# Transform

hourly_dataframe['year'] = hourly_dataframe['date'].dt.year
hourly_dataframe['month'] = hourly_dataframe['date'].dt.month
hourly_dataframe['day'] = hourly_dataframe['date'].dt.day
hourly_dataframe = pd.DataFrame(hourly_dataframe)
hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
hourly_dataframe['time'] = hourly_dataframe['date'].dt.strftime('%H:%M:%S')
hourly_dataframe = hourly_dataframe.drop('date', axis=1)

# Load

hourly_dataframe.to_csv("Weather.csv")
