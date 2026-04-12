from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RidershipRecord
from schemas import DemandRequest
from services.demand_model import train, predict
import pandas as pd

router = APIRouter()

@router.post("/demand")
def forecast_demand(req: DemandRequest, db: Session = Depends(get_db)):
    """Predict passenger demand for next N hours on a route."""
    rows = db.query(RidershipRecord)\
             .filter(RidershipRecord.route_id == req.route_id)\
             .all()

    if len(rows) < 10:
        raise HTTPException(
            status_code=400,
            detail="Need at least 10 ridership records to predict. Upload more data first."
        )

    df = pd.DataFrame([{
        "route_id":  r.route_id,
        "timestamp": r.timestamp,
        "passengers": r.passengers
    } for r in rows])

    model   = train(df)
    forecast = predict(model, req.route_id, req.horizon_hours)
    peak    = max(forecast, key=lambda x: x["predicted_passengers"])

    return {
        "route_id":       req.route_id,
        "horizon_hours":  req.horizon_hours,
        "peak_hour":      peak,
        "forecast":       forecast
    }