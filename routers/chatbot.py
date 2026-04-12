from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import SimulationResult
from services.chatbot_context import build_context
from pydantic import BaseModel
from typing import Optional
import os, requests as req

router = APIRouter()

class ChatRequest(BaseModel):
    message:  str
    route_id: Optional[int] = None  # optional — narrows context if provided

@router.post("/ask")
def ask(chat: ChatRequest, db: Session = Depends(get_db)):
    """
    Ask the AI anything about routes, schedules, demand,
    simulations, or carbon footprint.
    Pulls live data from the database before every answer.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY missing from .env file. Add it and restart the server."
        )

    system_prompt = build_context(db)

    # If a specific route_id was sent, append it as user hint
    user_message = chat.message
    if chat.route_id:
        user_message += f"\n\n[Context: user is asking about Route {chat.route_id}]"

    response = req.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
        json={
            "model":      "claude-haiku-4-5-20251001",
            "max_tokens": 350,
            "system":     system_prompt,
            "messages":   [{"role": "user", "content": user_message}],
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Claude API returned {response.status_code}: {response.text}"
        )

    answer = response.json()["content"][0]["text"]
    return {
        "question": chat.message,
        "answer":   answer,
        "model":    "claude-haiku-4-5-20251001",
    }

@router.get("/suggestions")
def suggestions(db: Session = Depends(get_db)):
    """
    Returns suggested questions based on what data is actually
    in the system — useful for the frontend chat UI.
    """
    from models import Route, Schedule
    routes    = db.query(Route).all()
    has_sched = db.query(Schedule).count() > 0
    has_sims  = db.query(SimulationResult).count() > 0

    questions = []

    for r in routes[:3]:
        questions.append(f"What is the busiest time on {r.name}?")
        questions.append(f"How many trips does {r.name} run per day?")

    if has_sched:
        questions.append("Which route has the highest frequency?")
        questions.append("What time does the first bus run?")

    if has_sims:
        questions.append("What did the last simulation show?")
        questions.append("Which simulation had the best overcrowding reduction?")

    questions.append("Which route has the most passengers on average?")
    questions.append("Which route should be optimized first?")

    return {
        "suggestions": questions[:8]   # return top 8
    }