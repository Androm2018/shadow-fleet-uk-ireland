import requests

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

# Test VOSTOCHNY PROSPECT - we know this works
url = "https://api.datalastic.com/api/v0/vessel_history"
params = {
    "api-key": "4ce425ec-75d1-4678-b879-d44597ba1b2f",
    "mmsi": "273611590",
    "from": "2024-01-01",
    "to":   "2024-01-31",
}
r = requests.get(url, params=params, timeout=30)
data = r.json().get('data', {})
positions = data.get('positions', [])
print(f"Total positions returned: {len(positions)}")
if positions:
    print(f"First position: {positions[0]}")
    print(f"Last position:  {positions[-1]}")
    # Show all unique lat/lon ranges
    lats = [float(p['lat']) for p in positions]
    lons = [float(p['lon']) for p in positions]
    print(f"Lat range: {min(lats):.2f} to {max(lats):.2f}")
    print(f"Lon range: {min(lons):.2f} to {max(lons):.2f}")
