import requests

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

url = "https://api.datalastic.com/api/v0/vessel_history"
params = {
    "api-key": "4ce425ec-75d1-4678-b879-d44597ba1b2f",
    "mmsi": "273611590",
    "from": "2024-01-01",
    "to": "2024-01-07"
}
r = requests.get(url, params=params, timeout=30)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
