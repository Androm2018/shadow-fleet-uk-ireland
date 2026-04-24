import sqlite3, pandas as pd, requests, time

API_KEY = "4ce425ec-75d1-4678-b879-d44597ba1b2f"

UK_BOX = {"lat": (49.0, 61.0), "lon": (-11.0, 3.0)}

ZONES = {
    "Dover_Strait":    {"lat": (50.8, 51.5), "lon": (-1.5,  2.0)},
    "English_Channel": {"lat": (49.5, 51.0), "lon": (-5.5, -1.5)},
    "Irish_Sea":       {"lat": (51.5, 55.0), "lon": (-6.5, -3.0)},
    "North_Channel":   {"lat": (54.5, 55.5), "lon": (-6.5, -4.5)},
    "St_Georges":      {"lat": (51.0, 52.5), "lon": (-6.5, -4.5)},
    "Fair_Isle":       {"lat": (59.0, 60.5), "lon": (-3.5,  0.0)},
}

MONTHS = [
    ("2025-01-01","2025-01-31"),("2025-02-01","2025-02-28"),
    ("2025-03-01","2025-03-31"),("2025-04-01","2025-04-24"),
]

def classify_zone(lat, lon):
    for zone, bounds in ZONES.items():
        if bounds['lat'][0] <= lat <= bounds['lat'][1] and \
           bounds['lon'][0] <= lon <= bounds['lon'][1]:
            return zone
    return "UK_Other"

conn = sqlite3.connect("Vessels1.db")
vessels = pd.read_sql("SELECT mmsi, name FROM vessels", conn)
conn.close()
print(f"Watchlist: {len(vessels)} vessels | {len(MONTHS)} months to query")

all_records = []

for date_from, date_to in MONTHS:
    print(f"\n=== {date_from} to {date_to} ===")
    month_hits = 0
    for i, row in vessels.iterrows():
        mmsi = str(row['mmsi']).strip()
        name = str(row['name']).strip()
        params = {"api-key": API_KEY, "mmsi": mmsi, "from": date_from, "to": date_to}
        try:
            r = requests.get("https://api.datalastic.com/api/v0/vessel_history",
                           params=params, timeout=30)
            if r.status_code == 402:
                print("Out of credits — stopping")
                break
            positions = r.json().get('data', {}).get('positions', [])
            uk_hits = [p for p in positions
                      if UK_BOX['lat'][0] <= float(p.get('lat',0)) <= UK_BOX['lat'][1]
                      and UK_BOX['lon'][0] <= float(p.get('lon',0)) <= UK_BOX['lon'][1]]
            if uk_hits:
                for p in uk_hits:
                    p['mmsi'] = mmsi
                    p['vessel_name'] = name
                    p['Zone'] = classify_zone(float(p['lat']), float(p['lon']))
                    p['month'] = date_from[:7]
                all_records.extend(uk_hits)
                month_hits += len(uk_hits)
                print(f"  HIT: {name} — {len(uk_hits)} pings in UK/Irish waters")
        except Exception as e:
            pass
        time.sleep(0.25)
    print(f"  Month total: {month_hits} UK/Irish pings")
    # Save after each month
    if all_records:
        pd.DataFrame(all_records).to_csv("uk_ireland_shadow_fleet.csv", index=False)
        print(f"  Running total saved: {len(all_records)} records")

if all_records:
    df = pd.DataFrame(all_records)
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total UK/Irish pings: {len(df):,}")
    print(f"Unique vessels: {df['mmsi'].nunique()}")
    print(f"\nZone breakdown:")
    print(df.groupby('Zone')['mmsi'].count().sort_values(ascending=False).to_string())
    print(f"\nTop vessels:")
    print(df.groupby(['mmsi','vessel_name'])['Zone'].count().sort_values(ascending=False).head(15).to_string())
else:
    print("\nNo shadow fleet vessels found in UK/Irish waters")
