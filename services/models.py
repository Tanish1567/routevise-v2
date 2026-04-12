from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
from datetime import datetime

class Route(Base):
    __tablename__ = "routes"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)
    zone        = Column(String)
    stops       = Column(JSON)
    distance_km = Column(Float)
    created_at  = Column(DateTime, default=datetime.utcnow)

class RidershipRecord(Base):
    __tablename__ = "ridership"
    id         = Column(Integer, primary_key=True, index=True)
    route_id   = Column(Integer)
    timestamp  = Column(DateTime)
    passengers = Column(Integer)
    vehicle_id = Column(String, default="unknown")

class Schedule(Base):
    __tablename__ = "schedules"
    id           = Column(Integer, primary_key=True, index=True)
    route_id     = Column(Integer)
    departures   = Column(JSON)
    frequency    = Column(Integer)
    generated_at = Column(DateTime, default=datetime.utcnow)

class SimulationResult(Base):
    __tablename__ = "simulations"
    id           = Column(Integer, primary_key=True, index=True)
    route_ids    = Column(JSON)
    modification = Column(String)
    params       = Column(JSON)
    result       = Column(JSON)
    created_at   = Column(DateTime, default=datetime.utcnow)