import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database import engine, Base
from routers import (
    ingestion, predict, optimize, schedule, simulate,
    analytics, load_balancer, multimodal, carbon, chatbot
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RouteWise — Intelligent Public Transport API",
    description="PS-4 | Demand prediction, optimization, scheduling, carbon tracking, AI chatbot",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router,     prefix="/routes",     tags=["📥 Data Ingestion"])
app.include_router(predict.router,       prefix="/predict",    tags=["🔮 Demand Prediction"])
app.include_router(optimize.router,      prefix="/routes",     tags=["🗺️ Route Optimization"])
app.include_router(schedule.router,      prefix="/schedule",   tags=["📅 Smart Scheduling"])
app.include_router(simulate.router,      prefix="/simulate",   tags=["🧪 What-If Simulation"])
app.include_router(analytics.router,     prefix="/analytics",  tags=["📊 Analytics"])
app.include_router(load_balancer.router, prefix="/vehicles",   tags=["⚖️ Load Balancing"])
app.include_router(multimodal.router,    prefix="/multimodal", tags=["🚇 Multi-Modal"])
app.include_router(carbon.router,        prefix="/carbon",     tags=["🌱 Carbon Footprint"])
app.include_router(chatbot.router,       prefix="/chat",       tags=["🤖 AI Chatbot"])

@app.get("/", tags=["Frontend"])
def root():
    landing = BASE_DIR / "routewise.html"
    if landing.exists():
        return FileResponse(landing)
    return {"status": "RouteWise API is running", "docs": "/docs", "version": "2.0.0"}

@app.get("/app", tags=["Frontend"])
def app_dashboard():
    dashboard = BASE_DIR / "index1.html"
    if dashboard.exists():
        return FileResponse(dashboard)
    return {"error": "Dashboard file not found", "expected": str(dashboard)}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "RouteWise API is running", "docs": "/docs", "version": "2.0.0"}
