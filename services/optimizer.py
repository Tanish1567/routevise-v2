import math

def haversine_distance(stop1: dict, stop2: dict) -> float:
    """Real-world distance in km between two lat/lon points."""
    R = 6371
    lat1, lon1 = math.radians(stop1["lat"]), math.radians(stop1["lon"])
    lat2, lon2 = math.radians(stop2["lat"]), math.radians(stop2["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def nearest_neighbor_route(stops: list) -> list:
    """
    Greedy nearest-neighbor algorithm.
    Returns stops in optimized visit order.
    """
    if not stops:
        return []

    unvisited = list(range(1, len(stops)))
    path = [0]
    current = 0

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda i: haversine_distance(stops[current], stops[i])
        )
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return path

def split_into_vehicle_routes(stops: list, num_vehicles: int) -> list:
    """Split optimized stop order across multiple vehicles."""
    optimized_order = nearest_neighbor_route(stops)
    ordered_stops = [stops[i] for i in optimized_order]

    chunk_size = max(1, len(ordered_stops) // num_vehicles)
    vehicle_routes = []

    for i in range(num_vehicles):
        chunk = ordered_stops[i * chunk_size : (i + 1) * chunk_size]
        if chunk:
            vehicle_routes.append({
                "vehicle_id": f"V{i+1}",
                "stops": chunk,
                "stop_count": len(chunk)
            })

    return vehicle_routes

def calculate_total_distance(stops: list) -> float:
    """Total route distance in km."""
    total = 0
    for i in range(len(stops) - 1):
        total += haversine_distance(stops[i], stops[i+1])
    return round(total, 2)