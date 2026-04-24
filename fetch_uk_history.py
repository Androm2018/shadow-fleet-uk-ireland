import sqlite3, pandas as pd, requests, time

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

# UK/Irish waters bounding box for local filtering
UK_IRELAND = {"lat": (49.0, 61.0), "lon": (-11.0, 3.0)}

# Date range
DATE_FROM = "2024-01-01"
DATE_TO   = "2025-10-31"

# Chokepoint zones for classification
ZONES = {
    "Dover_Strait":    {"lat": (50.8, 51.5), "lon": (-1.5,  2.0)},
    "English_Channel": {"lat": (49.5, 51.0), "lon": (-5.5, -1.5)},
    "Irish_Sea":       {"lat": (51.5, 55.0), "lon": (-6.5, -3.0)},
    "North_Channel":   {"lat": (54.5, 55.5), "lon": (-6.5, -4.5)},
    "St_Georges":      {"lat": (51.0, 52.5), "lon": (-6.5, -4.5)},
    "Fair_Isle":       {"lat": (59.0, 60.5), "lon": (-3.5,  0.0)},
}

def classify_zone(lat, lon):
    for zone, bounds in ZONES.items():
        if bounds['lat'][0] <= lat <= bounds['lat'][1] and \
           bounds['lon'][0] <= lon <= bounds['lon'][1]:
            return zone
    return "UK_Other"

conn = sqlite3.connect("Vessels1.db")
vessels = pd.read_sql("SELECT mmsi, name FROM vessels", conn)
conn.close()
print(f"Watchlist: {len(vessels)} vessels")

all_records = []
no_data = 0
errors = 0

for i, row in vessels.iterrows():
    mmsi = str(row['mmsi']).strip()
    name = str(row['name']).strip()

    url = "https://api.datalastic.com/api/v0/vessel_history"
    params = {
        "api-key": "4ce425ec-75d1-4678-b879-d44597ba1b2f",
        "mmsi":    mmsi,
        "from":    DATE_FROM,
        "to":      DATE_TO,
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json().get('data', {})
            positions = data.get('positions', [])
            # Filter to UK/Irish waters
            uk_positions = [
                p for p in positions
                if UK_IRELAND['lat'][0] <= float(p.get('lat', 0)) <= UK_IRELAND['lat'][1]
                and UK_IRELAND['lon'][0] <= float(p.get('lon', 0)) <= UK_IRELAND['lon'][1]
            ]
            if uk_positions:
                for p in uk_positions:
                    p['mmsi'] = mmsi
                    p['vessel_name'] = name
                    p['Zone'] = classify_zone(float(p['lat']), float(p['lon']))
                all_records.extend(uk_positions)
                print(f"  [{i+1}/{len(vessels)}] {name}: {len(uk_positions)} UK/Irish pings")
            else:
                no_data += 1
        elif r.status_code == 402:
            print(f"Out of credits at vessel {i+1}/{len(vessels)}")
            break
        else:
            errors += 1
    except Exception as e:
        errors += 1
        print(f"  Error on {mmsi}: {e}")

    # Save progress every 50 vessels
    if i % 50 == 0 and all_records:
        pd.DataFrame(all_records).to_csv("uk_ireland_shadow_fleet.csv", index=False)
        print(f"  Progress saved: {len(all_records)} records so far")

    time.sleep(0.3)

if all_records:
    df = pd.DataFrame(all_records)
    df.to_csv("uk_ireland_shadow_fleet.csv", index=False)
    print(f"\nDone! {len(df):,} UK/Irish pings saved")
    print(f"Unique vessels: {df['mmsi'].nunique()}")
    print(f"Zone breakdown:\n{df.groupby('Zone')['mmsi'].count().sort_values(ascending=False).to_string()}")
    print(f"\nNo UK/Irish data: {no_data} vessels")
    print(f"Errors: {errors}")
else:
    print("No shadow fleet vessels found in UK/Irish waters")
