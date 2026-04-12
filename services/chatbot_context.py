from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Route, RidershipRecord, Schedule, SimulationResult

def build_context(db: Session) -> str:
    """
    Pulls live data from the database and formats it as a
    system prompt so the AI always answers with current info.
    Covers: route info, schedules, demand patterns, simulations.
    """
    routes      = db.query(Route).all()
    sim_count   = db.query(SimulationResult).count()
    rec_count   = db.query(RidershipRecord).count()

    # ── Route + schedule + demand summary ────────────────────────
    route_lines = []
    for r in routes:
        # Average and peak passengers
        stats = db.query(
            func.avg(RidershipRecord.passengers).label("avg"),
            func.max(RidershipRecord.passengers).label("peak"),
            func.min(RidershipRecord.passengers).label("low"),
        ).filter(RidershipRecord.route_id == r.id).first()

        avg_pax  = int(stats.avg)  if stats.avg  else 0
        peak_pax = int(stats.peak) if stats.peak else 0
        low_pax  = int(stats.low)  if stats.low  else 0

        # Schedule info
        sched = db.query(Schedule).filter(Schedule.route_id == r.id)\
                  .order_by(Schedule.generated_at.desc()).first()
        if sched:
            sched_info = (f"frequency every {sched.frequency} min, "
                          f"{len(sched.departures)} trips/day, "
                          f"first bus {sched.departures[0]}, "
                          f"last bus {sched.departures[-1]}")
        else:
            sched_info = "no schedule generated yet"

        route_lines.append(
            f"  Route {r.id} | '{r.name}' | Zone: {r.zone} | "
            f"Distance: {r.distance_km}km | "
            f"Avg passengers: {avg_pax} | Peak: {peak_pax} | Low: {low_pax} | "
            f"Schedule: {sched_info}"
        )

    # ── Recent simulations ────────────────────────────────────────
    recent_sims = db.query(SimulationResult)\
                    .order_by(SimulationResult.created_at.desc())\
                    .limit(5).all()
    sim_lines = []
    for s in recent_sims:
        sim_lines.append(
            f"  Sim #{s.id}: type='{s.modification}' | "
            f"routes={s.route_ids} | "
            f"result summary: {list(s.result.values())[0] if s.result else 'N/A'}"
        )

    return f"""You are RouteWise AI — a smart assistant built into an intelligent public transport system.
You answer questions about routes, schedules, demand patterns, and simulation results.
Always use the live data below. Be concise (under 120 words). Suggest actions when relevant.

━━ LIVE SYSTEM DATA ━━
Total routes: {len(routes)}
Ridership records in DB: {rec_count:,}
Simulations run: {sim_count}

━━ ROUTES (live) ━━
{chr(10).join(route_lines) if route_lines else "No routes registered yet."}

━━ RECENT SIMULATIONS (last 5) ━━
{chr(10).join(sim_lines) if sim_lines else "No simulations run yet."}

━━ WHAT YOU CAN ANSWER ━━
- Route info: stops, zones, distance, which is busiest
- Schedules: frequency, first/last bus, trips per day
- Demand: peak hours, average passengers, low-demand periods
- Simulations: what was tested, what results came back
- Recommendations: which route to optimize, when to add frequency

Do NOT make up numbers. Only use the data above.
If something is not in the data, say you don't have that info yet."""