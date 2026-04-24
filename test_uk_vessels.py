import requests, time

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

TEST_VESSELS = {
    "273611590": "VOSTOCHNY PROSPECT",
    "352179000": "HORAE",
    "215375000": "GEORGIA",
    "352001887": "SILVAR",
    "372669000": "KATIUSKA",
    "423530100": "ZANGAZUR",
}

UK_BOX = {"lat": (49.0, 61.0), "lon": (-11.0, 3.0)}

for mmsi, name in TEST_VESSELS.items():
    url = "https://api.datalastic.com/api/v0/vessel_history"
    params = {"api-key": API_KEY, "mmsi": mmsi, "from": "2025-01-01", "to": "2025-10-31"}
    r = requests.get(url, params=params, timeout=30)
    positions = r.json().get('data', {}).get('positions', [])
    if not positions:
        print(f"{name}: no positions returned")
        time.sleep(0.5)
        continue
    uk_hits = [p for p in positions
               if UK_BOX['lat'][0] <= float(p.get('lat',0)) <= UK_BOX['lat'][1]
               and UK_BOX['lon'][0] <= float(p.get('lon',0)) <= UK_BOX['lon'][1]]
    all_lats = [float(p['lat']) for p in positions]
    all_lons = [float(p['lon']) for p in positions]
    print(f"{name}: {len(positions)} pings | {len(uk_hits)} UK/Irish hits | lat {min(all_lats):.1f} to {max(all_lats):.1f} | lon {min(all_lons):.1f} to {max(all_lons):.1f}")
    time.sleep(0.5)
