from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Route, RidershipRecord, Schedule

router = APIRouter()

@router.get("/heatmap")
def demand_heatmap(db: Session = Depends(get_db)):
    """Average passengers per route — used for heatmap visualization."""
    data = db.query(
        RidershipRecord.route_id,
        func.avg(RidershipRecord.passengers).label("avg"),
        func.max(RidershipRecord.passengers).label("peak"),
        func.count(RidershipRecord.id).label("records")
    ).group_by(RidershipRecord.route_id).all()

    return [
        {
            "route_id":     row.route_id,
            "avg_passengers": round(row.avg, 1),
            "peak_passengers": row.peak,
            "data_points":  row.records
        }
        for row in data
    ]

@router.get("/routes/map")
def routes_geojson(db: Session = Depends(get_db)):
    """GeoJSON for map visualization."""
    routes = db.query(Route).all()
    features = [
        {
            "type": "Feature",
            "properties": {"id": r.id, "name": r.name, "zone": r.zone},
            "geometry": {
                "type": "LineString",
                "coordinates": [[s["lon"], s["lat"]] for s in r.stops]
            }
        }
        for r in routes
    ]
    return {"type": "FeatureCollection", "features": features}

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    """Overall system summary for dashboard."""
    total_routes    = db.query(Route).count()
    total_records   = db.query(RidershipRecord).count()
    total_schedules = db.query(Schedule).count()
    return {
        "total_routes":    total_routes,
        "ridership_records": total_records,
        "schedules_generated": total_schedules
    }