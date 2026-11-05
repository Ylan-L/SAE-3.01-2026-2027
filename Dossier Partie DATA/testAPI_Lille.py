import requests
# import json

URL = "https://climate-api.open-meteo.com/v1/climate"
params = {
    "latitude": 50.63,
    "longitude": 3.06,
    "start_date": "1950-01-01",
    "end_date": "1950-12-31",
    "models": "MRI_AGCM3_2_S",
    "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum",
}

r = requests.get(URL, params=params, timeout=10)
print("Statut HTTP :", r.status_code)
print("URL appelée :", r.url)
# print(json.dumps(r.json(), indent=2, ensure_ascii=False))
