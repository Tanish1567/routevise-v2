from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Route, RidershipRecord
from schemas import RouteCreate, RouteOut, RidershipUpload
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=RouteOut)
def register_route(route: RouteCreate, db: Session = Depends(get_db)):
    """Register a new bus/metro route."""
    obj = Route(
        name=route.name,
        zone=route.zone,
        stops=[s.dict() for s in route.stops],
        distance_km=route.distance_km
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/list")
def list_routes(db: Session = Depends(get_db)):
    """Get all registered routes."""
    routes = db.query(Route).all()
    return [{"id": r.id, "name": r.name, "zone": r.zone, "stops": r.stops} for r in routes]

@router.post("/ridership")
def upload_ridership(data: RidershipUpload, db: Session = Depends(get_db)):
    """Upload historical ridership records."""
    records = []
    for row in data.records:
        records.append(RidershipRecord(
            route_id=row.route_id,
            timestamp=datetime.strptime(row.timestamp, "%Y-%m-%d %H:%M:%S"),
            passengers=row.passengers,
            vehicle_id=row.vehicle_id
        ))
    db.bulk_save_objects(records)
    db.commit()
    return {"status": "success", "rows_saved": len(records)}