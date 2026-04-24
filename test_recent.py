import requests

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

url = "https://api.datalastic.com/api/v0/vessel_history"

# Try progressively shorter/more recent date ranges
for date_from, date_to in [
    ("2025-04-01", "2025-04-24"),
    ("2025-03-01", "2025-03-31"),
    ("2025-01-01", "2025-01-31"),
    ("2024-06-01", "2024-06-30"),
    ("2024-01-01", "2024-01-31"),
]:
    params = {"api-key": API_KEY, "mmsi": "273611590", "from": date_from, "to": date_to}
    r = requests.get(url, params=params, timeout=30)
    positions = r.json().get('data', {}).get('positions', [])
    print(f"{date_from} to {date_to}: {len(positions)} positions")
