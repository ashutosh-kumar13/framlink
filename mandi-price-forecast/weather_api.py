import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",),
)))

def get_coordinates(mandi, district, state):
    """
    Get latitude and longitude for a place using fallbacks for better reliability.
    """
    search_queries = [
        f"{mandi}, {state}",
        f"{district}, {state}",
        f"{state}, India"
    ]

    url = "https://geocoding-api.open-meteo.com/v1/search"

    for query in search_queries:
        params = {
            "name": query,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        try:
            response = session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    print(f"Geocoding success for: {query}")
                    return results[0]['latitude'], results[0]['longitude']
        except Exception as e:
            print(f"Geocoding error for {query}: {e}")

    return None, None

def get_weather_forecast(lat, lon):
    """
    Get 7-day weather forecast from Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    try:
        response = session.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('daily', {})
    except Exception as e:
        print(f"Weather fetch error: {e}")
    return {}

def analyze_weather_impact(weather_data, commodity):
    """
    Analyze how the forecasted weather might impact the price of a specific commodity.
    Returns a list of daily impact multipliers and a general description.
    """
    if not weather_data:
        return [1.0] * 7, "Weather data unavailable."

    daily_impacts = []
    total_precip = sum(weather_data.get('precipitation_sum', []))

    precip_list = weather_data.get('precipitation_sum', [])
    for p in precip_list:
        if p > 10:
            daily_impacts.append(1.05) # Significant impact
        elif p > 2:
            daily_impacts.append(1.02) # Minor impact
        else:
            daily_impacts.append(1.0)

    # Padding to 7 days if necessary
    while len(daily_impacts) < 7:
        daily_impacts.append(1.0)

    if total_precip > 20:
        desc = f"Heavy rain predicted ({total_precip:.1f}mm). Supply chain delays may cause a price increase."
    elif total_precip > 5:
        desc = f"Moderate rain predicted ({total_precip:.1f}mm). Prices might stay firm."
    else:
        desc = "Stable weather predicted. No significant impact on prices."

    return daily_impacts, desc
