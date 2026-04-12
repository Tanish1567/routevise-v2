def get_load_status(passengers: int, capacity: int) -> str:
    """Return load status based on occupancy percentage."""
    if capacity == 0:
        return "UNKNOWN"
    pct = (passengers / capacity) * 100
    if pct > 100:
        return "OVERCROWDED"
    elif pct >= 85:
        return "HIGH"
    elif pct >= 50:
        return "MODERATE"
    else:
        return "LOW"

def balance_passengers(vehicles: list, capacity_per_vehicle: int) -> dict:
    """
    Takes a list of vehicles with current passenger counts.
    Redistributes overflowing passengers to vehicles with space.
    """
    total_passengers = sum(v["passengers"] for v in vehicles)
    total_capacity   = len(vehicles) * capacity_per_vehicle

    if total_passengers > total_capacity:
        return {
            "status":           "INSUFFICIENT_FLEET",
            "message":          f"Total demand {total_passengers} exceeds fleet capacity {total_capacity}. Add more vehicles.",
            "vehicles_needed":  -(-total_passengers // capacity_per_vehicle)
        }

    # Separate into overcrowded and underloaded
    overcrowded = [v for v in vehicles if v["passengers"] > capacity_per_vehicle]
    underloaded = [v for v in vehicles if v["passengers"] <= capacity_per_vehicle]

    # Build a mutable working copy of underloaded vehicles
    underloaded_working = [
        {**v, "current_load": v["passengers"], "absorbed": 0}
        for v in underloaded
    ]

    # Collect all overflow into a pool
    overflow_pool = sum(v["passengers"] - capacity_per_vehicle for v in overcrowded)

    # Distribute overflow to underloaded vehicles greedily
    for v in underloaded_working:
        if overflow_pool <= 0:
            break
        space = capacity_per_vehicle - v["current_load"]
        absorb = min(space, overflow_pool)
        v["current_load"] += absorb
        v["absorbed"]     += absorb
        overflow_pool     -= absorb

    # Build final result list
    rebalanced = []

    for v in overcrowded:
        new_load = capacity_per_vehicle
        rebalanced.append({
            "vehicle_id":      v["vehicle_id"],
            "route_id":        v["route_id"],
            "original_load":   v["passengers"],
            "new_load":        new_load,
            "transferred_out": v["passengers"] - new_load,
            "status":          get_load_status(new_load, capacity_per_vehicle)
        })

    for v in underloaded_working:
        rebalanced.append({
            "vehicle_id":    v["vehicle_id"],
            "route_id":      v["route_id"],
            "original_load": v["passengers"],
            "new_load":      v["current_load"],
            "absorbed":      v["absorbed"],
            "status":        get_load_status(v["current_load"], capacity_per_vehicle)
        })

    overcrowded_after = len([v for v in rebalanced if v["status"] == "OVERCROWDED"])

    return {
        "status":             "BALANCED" if overflow_pool == 0 else "PARTIALLY_BALANCED",
        "total_passengers":   total_passengers,
        "total_capacity":     total_capacity,
        "occupancy_pct":      round((total_passengers / total_capacity) * 100, 1),
        "overcrowded_before": len(overcrowded),
        "overcrowded_after":  overcrowded_after,
        "vehicles":           rebalanced
    }