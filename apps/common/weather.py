import logging
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import WeatherCache

logger = logging.getLogger(__name__)

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

class WeatherService:
    @staticmethod
    def get_current_weather():
        """
        Retrieves current campus weather from cache if within 30 minutes,
        otherwise updates from Open-Meteo free API.
        Falls back seamlessly to local realistic data if offline.
        """
        cached = WeatherCache.objects.order_by('-fetched_at').first()
        now = timezone.now()

        if cached and (now - cached.fetched_at) < timedelta(minutes=30):
            return {
                'temperature': round(cached.temperature, 1),
                'humidity': round(cached.humidity, 1),
                'precipitation': cached.precipitation,
                'condition': cached.weather_description,
                'wind_speed': cached.wind_speed,
                'source': 'cache'
            }

        # Attempt to query Open-Meteo free API
        try:
            url = settings.WEATHER_API_BASE_URL
            params = {
                'latitude': settings.CAMPUS_LAT,
                'longitude': settings.CAMPUS_LNG,
                'current_weather': 'true',
                'hourly': 'relative_humidity_2m',
                'timezone': 'auto'
            }
            resp = requests.get(url, params=params, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                cw = data.get('current_weather', {})
                temp = float(cw.get('temperature', 26.5))
                wcode = int(cw.get('weathercode', 0))
                wind = float(cw.get('windspeed', 8.5))
                condition = WEATHER_CODE_MAP.get(wcode, "Pleasant")

                record = WeatherCache.objects.create(
                    temperature=temp,
                    humidity=65.0,
                    precipitation=0.0,
                    weather_code=wcode,
                    weather_description=condition,
                    wind_speed=wind
                )
                return {
                    'temperature': round(record.temperature, 1),
                    'humidity': round(record.humidity, 1),
                    'precipitation': record.precipitation,
                    'condition': record.weather_description,
                    'wind_speed': record.wind_speed,
                    'source': 'live_open_meteo'
                }
        except Exception as e:
            logger.warning(f"Open-Meteo request failed ({e}). Using robust local campus fallback.")

        # Fallback if no network or cache expired
        if cached:
            return {
                'temperature': round(cached.temperature, 1),
                'humidity': round(cached.humidity, 1),
                'precipitation': cached.precipitation,
                'condition': cached.weather_description,
                'wind_speed': cached.wind_speed,
                'source': 'cached_fallback'
            }

        return {
            'temperature': 25.0,
            'humidity': 60.0,
            'precipitation': 0.0,
            'condition': 'Partly cloudy',
            'wind_speed': 10.0,
            'source': 'offline_fallback'
        }
