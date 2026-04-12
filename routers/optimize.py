from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Route
from schemas import OptimizeRequest
from services.optimizer import split_into_vehicle_routes, calculate_total_distance

router = APIRouter()

@router.post("/optimize")
def optimize_route(req: OptimizeRequest, db: Session = Depends(get_db)):
    """Optimize stop order and split across vehicles."""
    route = db.query(Route).filter(Route.id == req.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    stops = route.stops
    if len(stops) < 2:
        raise HTTPException(status_code=400, detail="Route needs at least 2 stops")

    vehicle_routes = split_into_vehicle_routes(stops, req.max_vehicles)
    total_dist     = calculate_total_distance(stops)

    return {
        "route_id":         req.route_id,
        "route_name":       route.name,
        "total_distance_km": total_dist,
        "vehicles_used":    len(vehicle_routes),
        "vehicle_routes":   vehicle_routes
    }