from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import SimulationResult, Route
from schemas import SimulateRequest

router = APIRouter()

@router.post("")
def run_simulation(req: SimulateRequest, db: Session = Depends(get_db)):
    """What-If simulation — test changes without affecting live data."""

    result = {}

    if req.modification == "add":
        new_stops = req.params.get("stops", [])
        result = {
            "action":                        "add",
            "new_stops_count":               len(new_stops),
            "projected_daily_passengers":    len(new_stops) * 15,
            "estimated_coverage_increase_pct": round(len(new_stops) * 2.5, 1),
            "recommendation":                "Viable if demand > 200/day"
        }

    elif req.modification == "remove":
        result = {
            "action":                   "remove",
            "affected_route_ids":       req.route_ids,
            "estimated_displaced_pax":  len(req.route_ids) * 180,
            "alternative_routes":       [r for r in req.route_ids if r != req.route_ids[0]],
            "recommendation":           "Do NOT remove without alternative coverage"
        }

    elif req.modification == "change":
        new_freq = max(1, req.params.get("frequency", 20))  # never allow 0
        result = {
            "action":                          "change",
            "new_frequency_minutes":           new_freq,
            "projected_overcrowding_reduction": f"{min(40, 60 // new_freq * 10)}%",
            "extra_trips_per_day":             (60 // new_freq) * 18,
            "recommendation":                  "Approved — implement during peak hours only"
        }

    else:
        result = {"error": "modification must be add | remove | change"}

    # Save simulation to DB
    sim = SimulationResult(
        route_ids=req.route_ids,
        modification=req.modification,
        params=req.params,
        result=result
    )
    db.add(sim)
    db.commit()

    return {"simulation_id": sim.id, "result": result}