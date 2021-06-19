from requests import get
from os import environ
from typing import List, Union
from time import sleep

API_KEY = environ['API_KEY']
API_URL = 'https://api.openweathermap.org/data/2.5/weather'


def get_weather(city: str) -> Union[dict, None]:
    """Return dict with current weather data for given city or None if city name is invalid."""
    query_params = {'q': city, 'units': 'metric', 'appid': API_KEY}
    response = get(API_URL, params=query_params)

    if response.status_code == 200:
        return response.json().get('main')


def get_group_weather(cities: List[str]) -> dict:
    """Return dict with current weather data for given city list."""
    data = {}
    for city in cities:
        sleep(5)  # long processing simulation
        data[city] = get_weather(city)

    print(data)  # TODO change to writing into database
    return data
