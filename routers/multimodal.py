from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Schedule

router = APIRouter()

@router.get("/connections")
def get_modal_connections(db: Session = Depends(get_db)):
    """Shows all routes that have schedules — potential connection points."""
    schedules = db.query(Schedule).all()
    if not schedules:
        raise HTTPException(status_code=404, detail="No schedules found. Generate schedules first.")
    return [
        {
            "route_id":    s.route_id,
            "frequency":   s.frequency,
            "total_trips": len(s.departures),
            "first_trip":  s.departures[0] if s.departures else None,
            "last_trip":   s.departures[-1] if s.departures else None,
        }
        for s in schedules
    ]

@router.post("/sync")
def sync_two_routes(route_a: int, route_b: int, db: Session = Depends(get_db)):
    """
    Finds time windows where passengers can transfer between two routes
    with a 2-7 minute wait (includes walking buffer).
    """
    sched_a = db.query(Schedule).filter(Schedule.route_id == route_a)\
                .order_by(Schedule.generated_at.desc()).first()
    sched_b = db.query(Schedule).filter(Schedule.route_id == route_b)\
                .order_by(Schedule.generated_at.desc()).first()

    if not sched_a:
        raise HTTPException(status_code=404, detail=f"No schedule for route {route_a}")
    if not sched_b:
        raise HTTPException(status_code=404, detail=f"No schedule for route {route_b}")

    # Sort Route B times so the break optimization works correctly
    times_b = sorted([
        (int(t.split(":")[0]) * 60 + int(t.split(":")[1]), t)
        for t in sched_b.departures
    ])

    connections = []                              # ← inside function, correct indent

    for t_a in sched_a.departures:               # ← inside function, correct indent
        h_a, m_a = map(int, t_a.split(":"))
        mins_a = h_a * 60 + m_a

        for mins_b, t_b_str in times_b:
            wait = mins_b - mins_a
            if wait > 7:
                break                            # safe because times_b is sorted
            if 2 <= wait <= 7:
                connections.append({
                    "route_a_time": t_a,
                    "route_b_time": t_b_str,
                    "wait_minutes": wait
                })

    return {                                     # ← outside both loops, correct indent
        "route_a":           route_a,
        "route_b":           route_b,
        "total_connections": len(connections),
        "transfer_windows":  connections[:10],
        "status":            "Optimized" if len(connections) > 0 else "No Windows Found",
        "recommendation":    "Good sync" if len(connections) > 5 else "Consider adjusting frequency"
    }