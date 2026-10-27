from unittest.mock import patch, MagicMock
import requests
from services.weather_service import weather_service


def test_weather_service_successful_mock():
    """Verify weather service with mocked external API response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'current_weather': {
            'temperature': 22.5,
            'weathercode': 0,
            'windspeed': 10.2
        }
    }

    with patch('requests.get', return_value=mock_resp):
        res = weather_service.get_weather_for_city("New York")
        assert res['available'] is True
        assert res['temperature'] == 22.5
        assert 'Clear sky' in res['condition']
        assert 'Optimal weather' in res['delivery_impact']


def test_weather_service_timeout_handling():
    """Verify timeout is caught gracefully and returns friendly fallback."""
    with patch('requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
        res = weather_service.get_weather_for_city("London")
        assert res['available'] is False
        assert "temporarily timed out" in res['message']
        assert res['temperature'] is None
        assert "Deliveries proceeding" in res['message']


def test_weather_service_connection_error_handling():
    """Verify connection error fallback."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Network down")):
        res = weather_service.get_weather_for_city("Tokyo")
        assert res['available'] is False
        assert "unavailable" in res['message']


def test_weather_endpoint_checkout(client):
    """Verify /checkout/weather-check route."""
    response = client.get('/checkout/weather-check?city=Chicago')
    assert response.status_code == 200
    data = response.get_json()
    assert 'available' in data
    assert 'delivery_impact' in data
