import requests
import random
import math
from datetime import datetime, timedelta

BASE = "http://localhost:8000"

# ══════════════════════════════════════════════════════════
#  REALISTIC TRANSIT DATA GENERATOR
#  Mirrors patterns found in real Kaggle transit datasets:
#  - Mumbai BEST Bus data
#  - Delhi DTC ridership
#  - Pune PMPML passenger counts
# ══════════════════════════════════════════════════════════

print("🌱 RouteWise — Realistic Data Seeder")
print("=" * 45)

# ── Real Nagpur MSRTC-style routes ──────────────────────
ROUTES = [
    {
        "name": "Route 1 — Sitabuldi to Airport",
        "zone": "North",
        "distance_km": 18.5,
        "stops": [
            {"name": "Sitabuldi Bus Stand",   "lat": 21.1489, "lon": 79.0810},
            {"name": "Sadar",                 "lat": 21.1520, "lon": 79.0762},
            {"name": "Civil Lines",           "lat": 21.1572, "lon": 79.0695},
            {"name": "Shankar Nagar",         "lat": 21.1623, "lon": 79.0634},
            {"name": "Hingna Road",           "lat": 21.1310, "lon": 79.0530},
            {"name": "Dr Ambedkar Chowk",    "lat": 21.1180, "lon": 79.0490},
            {"name": "Airport Gate",          "lat": 21.0922, "lon": 79.0472},
        ]
    },
    {
        "name": "Route 2 — Railway Station to VNIT",
        "zone": "South",
        "distance_km": 9.2,
        "stops": [
            {"name": "Nagpur Railway Station","lat": 21.1503, "lon": 79.0920},
            {"name": "Itwari",               "lat": 21.1467, "lon": 79.0991},
            {"name": "Cotton Market",         "lat": 21.1412, "lon": 79.1023},
            {"name": "Gandhibagh",            "lat": 21.1378, "lon": 79.1067},
            {"name": "Dharampeth",            "lat": 21.1367, "lon": 79.0714},
            {"name": "VNIT Campus",           "lat": 21.1340, "lon": 79.0497},
        ]
    },
    {
        "name": "Route 3 — Wardha Road IT Corridor",
        "zone": "East",
        "distance_km": 22.1,
        "stops": [
            {"name": "Zero Mile",             "lat": 21.1458, "lon": 79.0882},
            {"name": "Ramdaspeth",            "lat": 21.1390, "lon": 79.0785},
            {"name": "Bajaj Nagar",           "lat": 21.1289, "lon": 79.0867},
            {"name": "Trimurti Nagar",        "lat": 21.1178, "lon": 79.0934},
            {"name": "Manewada",              "lat": 21.0998, "lon": 79.1012},
            {"name": "Besa",                  "lat": 21.0867, "lon": 79.1123},
            {"name": "Mihan SEZ Gate",        "lat": 21.0723, "lon": 79.1245},
        ]
    },
    {
        "name": "Route 4 — Kamptee Road Express",
        "zone": "West",
        "distance_km": 14.7,
        "stops": [
            {"name": "Mahal Bus Stand",       "lat": 21.1501, "lon": 79.0943},
            {"name": "Nandanvan",             "lat": 21.1580, "lon": 79.1034},
            {"name": "Kalamna",               "lat": 21.1672, "lon": 79.1156},
            {"name": "Bhandara Road",         "lat": 21.1745, "lon": 79.1278},
            {"name": "Kamptee",               "lat": 21.2123, "lon": 79.1934},
        ]
    },
    {
        "name": "Route 5 — Outer Ring Road Metro Feeder",
        "zone": "Central",
        "distance_km": 31.0,
        "stops": [
            {"name": "Prajapati Nagar Metro", "lat": 21.1789, "lon": 79.0612},
            {"name": "Subhash Nagar",         "lat": 21.1701, "lon": 79.0534},
            {"name": "Indora",                "lat": 21.1623, "lon": 79.0456},
            {"name": "Automotive Square",     "lat": 21.1534, "lon": 79.0378},
            {"name": "Hingna",                "lat": 21.1334, "lon": 79.0256},
            {"name": "Butibori MIDC",         "lat": 21.1012, "lon": 79.0089},
        ]
    },
]

# ── Vehicle fleet ────────────────────────────────────────
VEHICLE_FLEET = {
    1: ["NGA-BUS-101", "NGA-BUS-102", "NGA-BUS-103"],
    2: ["NGA-BUS-201", "NGA-BUS-202"],
    3: ["NGA-BUS-301", "NGA-BUS-302", "NGA-BUS-303", "NGA-BUS-304"],
    4: ["NGA-BUS-401", "NGA-BUS-402"],
    5: ["NGA-BUS-501", "NGA-BUS-502", "NGA-BUS-503"],
}

# ══════════════════════════════════════════════════════════
#  REALISTIC DEMAND MODEL
#  Based on patterns from Mumbai BEST & Pune PMPML datasets
# ══════════════════════════════════════════════════════════

# Base demand per route (higher = busier corridor)
ROUTE_BASE_DEMAND = {1: 90, 2: 110, 3: 140, 4: 70, 5: 160}

# Hour-of-day multipliers (real transit pattern)
HOUR_MULTIPLIERS = {
    0: 0.05, 1: 0.03, 2: 0.02, 3: 0.02, 4: 0.05,
    5: 0.20, 6: 0.55, 7: 0.85, 8: 1.00, 9: 0.90,  # morning peak: 8am
    10: 0.60, 11: 0.55, 12: 0.70, 13: 0.65, 14: 0.50,
    15: 0.55, 16: 0.75, 17: 0.95, 18: 1.00, 19: 0.85,  # evening peak: 6pm
    20: 0.60, 21: 0.45, 22: 0.30, 23: 0.15,
}

# Day-of-week multipliers (Mon=0, Sun=6)
DAY_MULTIPLIERS = {
    0: 1.00,  # Monday    — full demand
    1: 1.05,  # Tuesday   — slightly busier
    2: 1.02,  # Wednesday
    3: 1.03,  # Thursday
    4: 1.08,  # Friday    — end of week surge
    5: 0.65,  # Saturday  — moderate weekend
    6: 0.45,  # Sunday    — low demand
}

# Month multipliers (school/college effect + festivals)
MONTH_MULTIPLIERS = {
    1: 1.02,  # January   — post new year normal
    2: 1.00,
    3: 0.95,  # March     — exam season, fewer commuters
    4: 0.90,  # April     — summer starts
    5: 0.85,  # May       — peak summer, low office
    6: 1.05,  # June      — monsoon, colleges reopen
    7: 1.08,  # July      — rainy season surge
    8: 1.10,  # August    — Independence Day, high activity
    9: 1.12,  # September — Ganesh festival, Nagpur especially
    10: 1.05, # October   — Diwali travel
    11: 0.98, # November
    12: 0.95, # December  — year end
}

# Weather effect on a given day (random but seeded for consistency)
def weather_factor(date):
    """Monsoon months have higher variance. Hot months reduce ridership."""
    month = date.month
    day_seed = date.toordinal()
    r = random.Random(day_seed)
    if month in [6, 7, 8]:     # monsoon — heavy rain reduces trips
        return r.uniform(0.70, 1.10)
    elif month in [4, 5]:       # summer heat
        return r.uniform(0.80, 1.00)
    else:
        return r.uniform(0.92, 1.08)

def passenger_count(route_id, hour, date, vehicle_count):
    """
    Realistic passenger count using multi-factor model.
    Mirrors Kaggle transit dataset distributions.
    """
    base     = ROUTE_BASE_DEMAND.get(route_id, 80)
    h_mult   = HOUR_MULTIPLIERS.get(hour, 0.3)
    d_mult   = DAY_MULTIPLIERS.get(date.weekday(), 1.0)
    m_mult   = MONTH_MULTIPLIERS.get(date.month, 1.0)
    w_factor = weather_factor(date)

    # Per-vehicle load (split total demand across running vehicles)
    raw = base * h_mult * d_mult * m_mult * w_factor
    per_vehicle = raw / max(1, vehicle_count)

    # Add realistic noise (±15%)
    noise = random.gauss(1.0, 0.12)
    final = int(per_vehicle * noise)

    # Hard bounds: 0 to 120 (bus capacity)
    return max(0, min(120, final))

# ══════════════════════════════════════════════════════════
#  STEP 1 — REGISTER ROUTES
# ══════════════════════════════════════════════════════════
print("\n📍 Registering routes...")
route_ids = []
for r in ROUTES:
    try:
        res = requests.post(f"{BASE}/routes/register", json=r)
        data = res.json()
        rid = data.get("id")
        if rid:
            route_ids.append(rid)
            print(f"   ✅ [{rid}] {r['name']} — {len(r['stops'])} stops, {r['distance_km']} km")
        else:
            print(f"   ⚠  {r['name']} — {data}")
    except Exception as e:
        print(f"   ✗  {r['name']} — {e}")

if not route_ids:
    print("\n✗ No routes registered. Is uvicorn running?")
    exit(1)

# ══════════════════════════════════════════════════════════
#  STEP 2 — GENERATE RIDERSHIP (30 days × routes × hours)
# ══════════════════════════════════════════════════════════
print(f"\n📊 Generating realistic ridership data (30 days)...")
print("   Using: peak-hour curves, weekday/weekend, monsoon, festival patterns")

base_date = datetime.now() - timedelta(days=30)
all_records = []

for route_idx, route_id in enumerate(route_ids, 1):
    fleet = VEHICLE_FLEET.get(route_idx, ["BUS-001", "BUS-002"])
    route_records = []

    for day_offset in range(30):
        current_date = base_date + timedelta(days=day_offset)

        # Only run buses during operating hours (5am to 11pm)
        for hour in range(5, 23):
            # Number of vehicles on road changes by time
            if hour in [7, 8, 9, 17, 18, 19]:      # peak — all vehicles
                active_vehicles = fleet
            elif hour in [0, 1, 2, 3, 4, 22, 23]:  # night — skeleton
                active_vehicles = fleet[:1]
            else:                                    # off-peak — half fleet
                active_vehicles = fleet[:max(1, len(fleet)//2)]

            for vehicle_id in active_vehicles:
                # Add slight time offset per vehicle (staggered departures)
                minute = random.randint(0, 55)
                ts = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                pax = passenger_count(
                    route_idx, hour, current_date,
                    len(active_vehicles)
                )

                route_records.append({
                    "route_id":   route_id,
                    "timestamp":  ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "passengers": pax,
                    "vehicle_id": vehicle_id
                })

    all_records.extend(route_records)
    print(f"   Route {route_id}: {len(route_records)} records generated")

# Upload in batches of 200
print(f"\n⬆  Uploading {len(all_records)} total records in batches...")
batch_size = 200
success = 0
for i in range(0, len(all_records), batch_size):
    batch = all_records[i:i+batch_size]
    try:
        res = requests.post(f"{BASE}/routes/ridership", json={"records": batch})
        if res.status_code == 200:
            success += len(batch)
    except Exception as e:
        print(f"   ✗ Batch {i//batch_size + 1} failed: {e}")

print(f"   ✅ {success} records uploaded successfully")

# ══════════════════════════════════════════════════════════
#  STEP 3 — GENERATE SMART SCHEDULES
# ══════════════════════════════════════════════════════════
print(f"\n📅 Generating smart schedules...")
for route_id in route_ids:
    try:
        res = requests.post(f"{BASE}/schedule/generate", json={
            "route_id": route_id,
            "base_frequency": 20
        })
        d = res.json()
        print(f"   ✅ Route {route_id}: every {d.get('frequency_minutes','?')} min — {d.get('total_trips_daily','?')} trips/day")
    except Exception as e:
        print(f"   ✗ Route {route_id}: {e}")

# ══════════════════════════════════════════════════════════
#  STEP 4 — OPTIMIZE ALL ROUTES
# ══════════════════════════════════════════════════════════
print(f"\n🗺  Optimizing routes...")
for route_id in route_ids:
    try:
        res = requests.post(f"{BASE}/routes/optimize", json={
            "route_id": route_id,
            "max_vehicles": 3
        })
        d = res.json()
        print(f"   ✅ Route {route_id}: {d.get('total_distance_km','?')} km, {d.get('vehicles_used','?')} vehicles")
    except Exception as e:
        print(f"   ✗ Route {route_id}: {e}")

# ══════════════════════════════════════════════════════════
#  STEP 5 — RUN SIMULATIONS
# ══════════════════════════════════════════════════════════
print(f"\n🧪 Running simulations...")
sims = [
    {"route_ids": route_ids[:2], "modification": "change", "params": {"frequency": 10},  "label": "Double frequency on Routes 1+2"},
    {"route_ids": route_ids[2:], "modification": "add",    "params": {"stops": [{"name":"New Stop","lat":21.14,"lon":79.08}]*3}, "label": "Add 3 stops to Routes 3-5"},
    {"route_ids": [route_ids[0]],"modification": "remove", "params": {},                  "label": "Simulate removing Route 1"},
]
for s in sims:
    try:
        res = requests.post(f"{BASE}/simulate", json=s)
        print(f"   ✅ {s['label']}")
    except Exception as e:
        print(f"   ✗ {s['label']}: {e}")

# ══════════════════════════════════════════════════════════
#  STEP 6 — SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 45)
print("🎉 Seeding complete!\n")

try:
    summary = requests.get(f"{BASE}/analytics/summary").json()
    heatmap = requests.get(f"{BASE}/analytics/heatmap").json()

    print(f"   Routes registered   : {summary.get('total_routes', '?')}")
    print(f"   Ridership records   : {summary.get('ridership_records', '?')}")
    print(f"   Schedules generated : {summary.get('schedules_generated', '?')}")
    print(f"\n   Demand by Route:")
    for h in heatmap:
        bar_len = int((h['avg_passengers'] / 200) * 20)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        level = "🔴 OVERCROWDED" if h['avg_passengers']>150 else "🟡 HIGH" if h['avg_passengers']>100 else "🟢 NORMAL"
        print(f"   Route {h['route_id']} [{bar}] {h['avg_passengers']:>3} avg pax — {level}")
except Exception as e:
    print(f"   Could not fetch summary: {e}")

print(f"\n   Open http://localhost:8000/docs to explore the API")
print(f"   Open index.html in browser to see the dashboard\n")
