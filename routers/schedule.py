from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Schedule, RidershipRecord
from schemas import ScheduleRequest
from services.scheduler import get_smart_frequency, generate_departure_times

router = APIRouter()

@router.post("/generate")
def generate_schedule(req: ScheduleRequest, db: Session = Depends(get_db)):
    """Auto-generate smart schedule based on demand."""
    # Get average passengers for this route
    rows = db.query(RidershipRecord)\
             .filter(RidershipRecord.route_id == req.route_id)\
             .all()

    avg_passengers = int(sum(r.passengers for r in rows) / len(rows)) if rows else 80

    frequency  = get_smart_frequency(avg_passengers, req.base_frequency)
    departures = generate_departure_times(frequency)

    sched = Schedule(
        route_id=req.route_id,
        departures=departures,
        frequency=frequency
    )
    db.add(sched)
    db.commit()

    return {
        "route_id":          req.route_id,
        "avg_passengers":    avg_passengers,
        "frequency_minutes": frequency,
        "total_trips_daily": len(departures),
        "sample_times":      departures[:5]
    }

@router.get("/view/{route_id}")
def view_schedule(route_id: int, db: Session = Depends(get_db)):
    sched = db.query(Schedule)\
              .filter(Schedule.route_id == route_id)\
              .order_by(Schedule.generated_at.desc())\
              .first()
    if not sched:
        raise HTTPException(status_code=404, detail="No schedule generated yet")
    return sched