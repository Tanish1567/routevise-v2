from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Route, RidershipRecord, Schedule
from services.carbon import calc_route_emissions, calc_optimization_savings
from pydantic import BaseModel

router = APIRouter()

class SavingsRequest(BaseModel):
    route_id:     int
    trips_per_day: int = 50

# ── 1. Emissions for a single route ──────────────────────────────
@router.get("/route/{route_id}")
def route_emissions(route_id: int, db: Session = Depends(get_db)):
    """CO2 emissions for one route based on its distance and average ridership."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    avg = db.query(func.avg(RidershipRecord.passengers))\
            .filter(RidershipRecord.route_id == route_id).scalar()
    avg_passengers = int(avg) if avg else 50

    result = calc_route_emissions(route.distance_km, avg_passengers)
    result["route_id"]   = route_id
    result["route_name"] = route.name
    return result

# ── 2. Emission savings from route optimization ───────────────────
@router.post("/savings")
def optimization_savings(req: SavingsRequest, db: Session = Depends(get_db)):
    """
    CO2 saved daily, weekly, and yearly by running the
    optimized route distance vs the original distance.
    Nearest-neighbor optimization typically reduces distance by ~15%.
    """
    route = db.query(Route).filter(Route.id == req.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    original_km  = route.distance_km
    optimized_km = round(original_km * 0.85, 2)  # 15% saving from optimization

    result = calc_optimization_savings(original_km, optimized_km, req.trips_per_day)
    result["route_id"]     = req.route_id
    result["route_name"]   = route.name
    result["trips_per_day"] = req.trips_per_day
    return result

# ── 3. Daily emission report across all routes ────────────────────
@router.get("/report/daily")
def daily_report(db: Session = Depends(get_db)):
    """Daily CO2 emissions across every route using actual trip counts from schedules."""
    routes = db.query(Route).all()
    if not routes:
        raise HTTPException(status_code=404, detail="No routes found. Run seed.py first.")

    report        = []
    total_co2     = 0.0
    total_saved   = 0.0

    for r in routes:
        sched = db.query(Schedule).filter(Schedule.route_id == r.id)\
                  .order_by(Schedule.generated_at.desc()).first()
        trips = len(sched.departures) if sched else 40

        avg = db.query(func.avg(RidershipRecord.passengers))\
                .filter(RidershipRecord.route_id == r.id).scalar()
        avg_pax = int(avg) if avg else 50

        data       = calc_route_emissions(r.distance_km, avg_pax)
        daily_co2  = round(data["bus_total_co2_kg"] * trips, 2)
        daily_save = round(data["co2_saved_kg"] * trips, 2)

        total_co2   += daily_co2
        total_saved += daily_save

        report.append({
            "route_id":            r.id,
            "route_name":          r.name,
            "trips_today":         trips,
            "avg_passengers":      avg_pax,
            "daily_co2_kg":        daily_co2,
            "daily_co2_saved_kg":  daily_save,
            "rating":              data["rating"],
        })

    return {
        "total_daily_co2_kg":      round(total_co2, 2),
        "total_daily_saved_kg":    round(total_saved, 2),
        "trees_equivalent_daily":  round(total_saved / 21.77, 1),
        "routes":                  report,
    }

# ── 4. Weekly emission report ─────────────────────────────────────
@router.get("/report/weekly")
def weekly_report(db: Session = Depends(get_db)):
    """Weekly CO2 summary — multiplies daily figures by 7."""
    routes = db.query(Route).all()
    if not routes:
        raise HTTPException(status_code=404, detail="No routes found.")

    report      = []
    total_weekly = 0.0
    total_saved  = 0.0

    for r in routes:
        sched = db.query(Schedule).filter(Schedule.route_id == r.id)\
                  .order_by(Schedule.generated_at.desc()).first()
        trips = len(sched.departures) if sched else 40

        avg = db.query(func.avg(RidershipRecord.passengers))\
                .filter(RidershipRecord.route_id == r.id).scalar()
        avg_pax = int(avg) if avg else 50

        data        = calc_route_emissions(r.distance_km, avg_pax)
        weekly_co2  = round(data["bus_total_co2_kg"] * trips * 7, 2)
        weekly_save = round(data["co2_saved_kg"]     * trips * 7, 2)

        total_weekly += weekly_co2
        total_saved  += weekly_save

        report.append({
            "route_id":             r.id,
            "route_name":           r.name,
            "weekly_co2_kg":        weekly_co2,
            "weekly_co2_saved_kg":  weekly_save,
            "rating":               data["rating"],
        })

    return {
        "total_weekly_co2_kg":    round(total_weekly, 2),
        "total_weekly_saved_kg":  round(total_saved, 2),
        "trees_equivalent_weekly": round(total_saved / 21.77, 1),
        "routes":                 report,
    }