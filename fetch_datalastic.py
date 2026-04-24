import sqlite3, pandas as pd, requests, time, os

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

ZONES = {
    "Dover_Strait":    {"lat1": 50.8, "lon1": -1.5, "lat2": 51.5, "lon2":  2.0},
    "English_Channel": {"lat1": 49.5, "lon1": -5.5, "lat2": 51.0, "lon2": -1.5},
    "Irish_Sea":       {"lat1": 51.5, "lon1": -6.5, "lat2": 55.0, "lon2": -3.0},
    "North_Channel":   {"lat1": 54.5, "lon1": -6.5, "lat2": 55.5, "lon2": -4.5},
    "St_Georges":      {"lat1": 51.0, "lon1": -6.5, "lat2": 52.5, "lon2": -4.5},
    "Fair_Isle":       {"lat1": 59.0, "lon1": -3.5, "lat2": 60.5, "lon2":  0.0},
}

conn = sqlite3.connect("Vessels1.db")
vessels = pd.read_sql("SELECT mmsi, name FROM vessels", conn)
conn.close()
mmsi_set = set(vessels['mmsi'].astype(str).str.strip())
print(f"Watchlist: {len(mmsi_set)} vessels")

all_records = []

for zone_name, bounds in ZONES.items():
    print(f"\nQuerying {zone_name}...")
    url = "https://api.datalastic.com/api/v0/vessel_inradius"
    params = {
        "api-key":  "4ce425ec-75d1-4678-b879-d44597ba1b2f",
        "lat":      (bounds['lat1'] + bounds['lat2']) / 2,
        "lon":      (bounds['lon1'] + bounds['lon2']) / 2,
        "radius":   200,
    }
    r = requests.get(url, params=params, timeout=30)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get('data', [])
        print(f"  Total vessels in zone: {len(data)}")
        hits = [v for v in data if str(v.get('mmsi','')).strip() in mmsi_set]
        print(f"  Shadow fleet hits: {len(hits)}")
        for h in hits:
            h['Zone'] = zone_name
            all_records.append(h)
    else:
        print(f"  Error: {r.text[:200]}")
    time.sleep(1)

if all_records:
    df = pd.DataFrame(all_records)
    df.to_csv("uk_ireland_live.csv", index=False)
    print(f"\nSaved {len(df)} records")
    print(df[['mmsi','name','Zone']].to_string())
else:
    print("\nNo shadow fleet vessels currently in UK/Irish zones")
    print("(This is the live endpoint - try the historical approach next)")
