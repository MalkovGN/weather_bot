import requests
from functools import partial
from geopy.geocoders import Nominatim
from utils import weather_dict


def get_country(city):
    geolocator = Nominatim(user_agent='tg_weather')
    geocode = partial(geolocator.geocode, language='en')
    country = str(geocode(city)).split(', ')[-1]
    return country


def get_forecast(city, days_to_forecast, api_key):
    output = []
    country = get_country(city)
    response = requests.get(
        f'https://api.weatherbit.io/v2.0/forecast/daily?city={city}'
        f'&country={country},NC&key={api_key}&days={round(days_to_forecast)}'
    )
    data = response.json()

    city_name = data['city_name']
    for info in data['data']:
        date = info['datetime']
        temp = info['temp']
        description = weather_dict[info['weather']['code']]
        wind_spd = round(info['wind_spd'], 1)
        humidity = info['rh']
        one_day_forecast = f"На {date} в городе {city_name} ожидается температура {temp}°C, {description}.\n" \
                           f" Скорость ветра {wind_spd}м/с, влажность - {humidity}%"
        output.append(one_day_forecast)

    return output


def get_weather(city, api_key):
    country = get_country(city)
    response = requests.get(f'https://api.weatherbit.io/v2.0/current?city={city}&country={country},NC&key={api_key}')

    data = response.json()['data'][0]
    temp = data['temp']
    temp_feels_like = data['app_temp']
    wind_spd = round(data['wind_spd'], 1)
    humidity = data['rh']
    description = weather_dict[data['weather']['code']]

    return(
        f"Сейчас в городе {city.capitalize()} {description}, температура {temp}°C, ощущается, как {temp_feels_like}°C.\n"
        f"Скорость ветра {wind_spd}м/c. Влажность - {humidity}%"
    )
