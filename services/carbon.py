# Real-world emission factors (kg CO2 per passenger-km)
EMISSION_FACTORS = {
    "bus":  0.089,   # diesel bus, per passenger
    "car":  0.171,   # average petrol car, per km (single occupant)
}

BUS_CAPACITY = 80  # standard bus

def calc_route_emissions(distance_km: float, passengers: int) -> dict:
    """
    Emissions per route trip based on distance + actual passengers.
    Also calculates what the same journey would cost in car emissions.
    """
    bus_co2_total      = distance_km * EMISSION_FACTORS["bus"] * BUS_CAPACITY
    bus_co2_per_pax    = distance_km * EMISSION_FACTORS["bus"]
    car_co2_equivalent = distance_km * EMISSION_FACTORS["car"] * passengers
    co2_saved          = car_co2_equivalent - bus_co2_total
    occupancy_pct      = round((passengers / BUS_CAPACITY) * 100, 1)

    return {
        "distance_km":           round(distance_km, 2),
        "passengers":            passengers,
        "occupancy_pct":         occupancy_pct,
        "bus_total_co2_kg":      round(bus_co2_total, 3),
        "bus_per_passenger_kg":  round(bus_co2_per_pax, 3),
        "car_equivalent_co2_kg": round(car_co2_equivalent, 3),
        "co2_saved_kg":          round(co2_saved, 3),
        "trees_equivalent":      round(co2_saved / 21.77, 2),
        "rating":                _rating(bus_co2_per_pax),
    }

def calc_optimization_savings(
    original_km: float,
    optimized_km: float,
    trips_per_day: int
) -> dict:
    """CO2 saved by shortening the route through optimization."""
    daily_original  = original_km  * EMISSION_FACTORS["bus"] * BUS_CAPACITY * trips_per_day
    daily_optimized = optimized_km * EMISSION_FACTORS["bus"] * BUS_CAPACITY * trips_per_day
    daily_saved     = daily_original - daily_optimized
    yearly_saved    = daily_saved * 365

    return {
        "original_distance_km":    round(original_km, 2),
        "optimized_distance_km":   round(optimized_km, 2),
        "distance_reduced_km":     round(original_km - optimized_km, 2),
        "daily_co2_saved_kg":      round(daily_saved, 2),
        "weekly_co2_saved_kg":     round(daily_saved * 7, 2),
        "yearly_co2_saved_kg":     round(yearly_saved, 2),
        "yearly_trees_equivalent": round(yearly_saved / 21.77, 1),
    }

def _rating(co2_per_km: float) -> str:
    if co2_per_km < 0.05:   return "A — Excellent"
    elif co2_per_km < 0.09: return "B — Good"
    elif co2_per_km < 0.12: return "C — Average"
    else:                   return "D — Poor"