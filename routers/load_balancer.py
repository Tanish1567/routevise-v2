from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import RidershipRecord, Route
from services.load_balancer import balance_passengers, get_load_status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class VehicleLoad(BaseModel):
    vehicle_id: str
    route_id: int
    passengers: int

class LoadBalanceRequest(BaseModel):
    vehicles: List[VehicleLoad]
    capacity_per_vehicle: Optional[int] = 80   # standard bus capacity

@router.post("/balance")
def balance_vehicle_loads(req: LoadBalanceRequest):
    """
    Takes current vehicle loads and redistributes passengers
    to eliminate overcrowding across the fleet.
    """
    if len(req.vehicles) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 vehicles to balance load"
        )

    vehicles_data = [v.dict() for v in req.vehicles]
    result = balance_passengers(vehicles_data, req.capacity_per_vehicle)
    return result

@router.get("/status/{route_id}")
def get_route_load_status(route_id: int, db: Session = Depends(get_db)):
    """
    Get current load status for all vehicles on a route
    based on latest ridership records.
    """
    # Get latest record per vehicle for this route
    subquery = db.query(
        RidershipRecord.vehicle_id,
        func.max(RidershipRecord.timestamp).label("latest")
    ).filter(
        RidershipRecord.route_id == route_id
    ).group_by(RidershipRecord.vehicle_id).subquery()

    records = db.query(RidershipRecord).join(
        subquery,
        (RidershipRecord.vehicle_id == subquery.c.vehicle_id) &
        (RidershipRecord.timestamp  == subquery.c.latest)
    ).all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No ridership data found for this route"
        )

    capacity = 80  # standard bus capacity
    vehicles = [{
        "vehicle_id": r.vehicle_id,
        "route_id":   r.route_id,
        "passengers": r.passengers,
        "status":     get_load_status(r.passengers, capacity),
        "occupancy_pct": round((r.passengers / capacity) * 100, 1)
    } for r in records]

    overcrowded = [v for v in vehicles if v["status"] == "OVERCROWDED"]

    return {
        "route_id":         route_id,
        "total_vehicles":   len(vehicles),
        "overcrowded_count": len(overcrowded),
        "vehicles":         vehicles,
        "recommendation":   "Run /vehicles/balance to redistribute load" if overcrowded else "Fleet load is healthy"
    }