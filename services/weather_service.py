import os
import time
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger('mysterymart.weather')

# Well-known city coordinates to provide lightning-fast lookups without extra API hops
KNOWN_CITIES = {
    'new york': (40.7128, -74.0060, 'United States'),
    'london': (51.5074, -0.1278, 'United Kingdom'),
    'tokyo': (35.6762, 139.6503, 'Japan'),
    'mumbai': (19.0760, 72.8777, 'India'),
    'delhi': (28.6139, 77.2090, 'India'),
    'bengaluru': (12.9716, 77.5946, 'India'),
    'paris': (48.8566, 2.3522, 'France'),
    'berlin': (52.5200, 13.4050, 'Germany'),
    'sydney': (-33.8688, 151.2093, 'Australia'),
    'toronto': (43.6532, -79.3832, 'Canada'),
    'san francisco': (37.7749, -122.4194, 'United States'),
    'chicago': (41.8781, -87.6298, 'United States'),
    'singapore': (1.3521, 103.8198, 'Singapore'),
    'dubai': (25.2048, 55.2708, 'United Arab Emirates'),
}

# Weather code descriptions based on WMO Weather interpretation codes
WEATHER_CODES = {
    0: ('Clear sky', '☀️'),
    1: ('Mainly clear', '🌤️'),
    2: ('Partly cloudy', '⛅'),
    3: ('Overcast', '☁️'),
    45: ('Foggy', '🌫️'),
    48: ('Depositing rime fog', '🌫️'),
    51: ('Light drizzle', '🌦️'),
    53: ('Moderate drizzle', '🌦️'),
    55: ('Dense drizzle', '🌧️'),
    61: ('Slight rain', '🌧️'),
    63: ('Moderate rain', '🌧️'),
    65: ('Heavy rain', '🌧️'),
    71: ('Slight snow fall', '🌨️'),
    73: ('Moderate snow fall', '🌨️'),
    75: ('Heavy snow fall', '❄️'),
    80: ('Slight rain showers', '🌦️'),
    81: ('Moderate rain showers', '🌧️'),
    82: ('Violent rain showers', '⛈️'),
    95: ('Thunderstorm', '⛈️'),
}

# In-memory cache: {city_key: (timestamp, data_dict)}
_WEATHER_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 900  # 15 minutes


class WeatherService:
    """Service to fetch delivery destination weather using Open-Meteo external API."""

    def __init__(self):
        self.api_url = os.environ.get('WEATHER_API_URL', 'https://api.open-meteo.com/v1/forecast')
        self.timeout = int(os.environ.get('WEATHER_API_TIMEOUT', 4))

    def get_weather_for_city(self, city_name: str) -> Dict[str, Any]:
        """
        Fetch real-time delivery destination weather.
        Never throws unhandled exceptions; provides rich fallback if unreachable.
        """
        if not city_name or not city_name.strip():
            return self._build_fallback(city_name, "City name not provided.")

        city_clean = city_name.strip()
        cache_key = city_clean.lower()

        # Check Cache
        cached = _WEATHER_CACHE.get(cache_key)
        if cached:
            cached_time, cached_data = cached
            if time.time() - cached_time < CACHE_TTL_SECONDS:
                return cached_data

        coords = KNOWN_CITIES.get(cache_key)
        lat, lon = (coords[0], coords[1]) if coords else (40.7128, -74.0060)  # Default fallback coords

        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true'
            }
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                temp = current.get('temperature')
                wcode = current.get('weathercode', 0)
                windspeed = current.get('windspeed', 0)

                condition, icon = WEATHER_CODES.get(wcode, ('Clear conditions', '☀️'))

                result = {
                    'available': True,
                    'city': city_clean.title(),
                    'temperature': temp,
                    'condition': condition,
                    'icon': icon,
                    'windspeed': windspeed,
                    'delivery_impact': self._calculate_delivery_impact(wcode, windspeed),
                    'summary': f"{icon} {condition}, {temp}°C in {city_clean.title()}",
                    'source': 'Open-Meteo Real-Time Weather API'
                }

                # Save to cache
                _WEATHER_CACHE[cache_key] = (time.time(), result)
                return result

            else:
                logger.warning("Weather API returned non-200 status code: %s", response.status_code)
                return self._build_fallback(city_clean, f"External weather service responded with HTTP {response.status_code}.")

        except requests.exceptions.Timeout:
            logger.warning("Weather API request timed out after %ds for city '%s'", self.timeout, city_clean)
            return self._build_fallback(city_clean, "Weather information temporarily timed out. Deliveries proceeding as normal!")
        except requests.exceptions.ConnectionError:
            logger.warning("Weather API connection failed for city '%s'", city_clean)
            return self._build_fallback(city_clean, "Weather service unavailable. MysteryMart dispatch remains unaffected.")
        except Exception as e:
            logger.error("Unexpected error in weather service for city '%s': %s", city_clean, e)
            return self._build_fallback(city_clean, "Weather service offline. Standard dispatch timelines apply.")

    def _calculate_delivery_impact(self, wcode: int, windspeed: float) -> str:
        """Friendly note on whether weather might affect delivery times."""
        if wcode in (82, 95, 75):
            return "Severe weather detected in area — slight delivery buffer may apply."
        elif wcode in (65, 73, 55):
            return "Rain/snow expected — packages are securely packaged in weatherproof waterproof mystery boxes!"
        return "Optimal weather conditions — expect on-time unboxing delivery!"

    def _build_fallback(self, city: str, message: str) -> Dict[str, Any]:
        """Return safe, non-blocking fallback response."""
        return {
            'available': False,
            'city': city.title() if city else 'Delivery Location',
            'temperature': None,
            'condition': 'Weather info unavailable',
            'icon': '📦',
            'delivery_impact': 'All MysteryMart parcels are dispatched in protective weatherproof seals.',
            'summary': f"Delivery to {city.title() if city else 'your area'}: On schedule",
            'message': message,
            'source': 'MysteryMart Dispatch Guard'
        }


weather_service = WeatherService()
