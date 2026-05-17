import requests

lat = -33.4569
lon = -70.6483

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m","relative_humidity_2m","precipitation"],
    "timezone":"America/Santiago",
    "forecast_days":1
}

response = requests.get(url,params=params)
response_json = response.json()

print("pene")

