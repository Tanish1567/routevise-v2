from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Stop(BaseModel):
    name: str
    lat: float
    lon: float

class RouteCreate(BaseModel):
    name: str
    zone: str
    stops: List[Stop]
    distance_km: float

class RouteOut(BaseModel):
    id: int
    name: str
    zone: str
    distance_km: float
    class Config:
        from_attributes = True

class RidershipRow(BaseModel):
    route_id: int
    timestamp: str
    passengers: int
    vehicle_id: Optional[str] = "unknown"

class RidershipUpload(BaseModel):
    records: List[RidershipRow]

class DemandRequest(BaseModel):
    route_id: int
    horizon_hours: int = 24

class OptimizeRequest(BaseModel):
    route_id: int
    max_vehicles: int = 3

class ScheduleRequest(BaseModel):
    route_id: int
    base_frequency: int = 20

class SimulateRequest(BaseModel):
    route_ids: List[int]
    modification: str
    params: Dict[str, Any]

class SavingsRequest(BaseModel):
    route_id:      int
    trips_per_day: int = 50

class ChatRequest(BaseModel):
    message:  str
    route_id: Optional[int] = None