from datetime import date, timedelta
import random
from typing import List, Dict, Tuple, Literal
from fitness_app.models import WorkoutPlan, WorkoutDay, db, User
# If you already integrated a tiny ML earlier, you can import it here:
try:
    from ml_engine import predict_intensity  # (age, weight, height, gender, goal) -> ("Low/Medium/High", bmi)
except Exception:
    predict_intensity = None  # fallback to heuristic if not available

ExerciseItem = Dict[str, object]  # {name, sets?, reps?, minutes?, completed}

# --- Exercise banks ---
BANK = {
    "strength": [
        "Back squats", "Front squats", "Romanian deadlifts", "Deadlifts",
        "Bench press", "Overhead press", "Barbell rows", "Pull-ups", "Dips",
        "Goblet squats", "Walking lunges", "Kettlebell swings", "Plank"
    ],
    "cardio": [
        "Rower easy", "Incline walk", "Steady run", "Tempo run",
        "Cycling", "Elliptical", "Stair climber", "Swim"
    ]
}

def bmi_from_profile(u: User) -> float | None:
    if not (u.height_cm and u.weight_kg):
        return None
    h = max(u.height_cm, 1) / 100.0
    return round(u.weight_kg / (h*h), 1)

def intensity_from_profile(u: User, goal: Literal["Weight Loss","Muscle Gain","Endurance"]) -> str:
    # Prefer ML if provided
    if predict_intensity and u.age and u.weight_kg and u.height_cm and u.gender:
        label, _ = predict_intensity(u.age, u.weight_kg, u.height_cm, u.gender, goal)
        return label

    # Fallback heuristic by age & BMI
    bmi = bmi_from_profile(u) or 24.0
    if (u.age or 30) < 25 and bmi < 26: return "High"
    if (u.age or 35) > 45 or bmi > 30:  return "Low"
    return "Medium"

def preset_volume(intensity: str) -> Tuple[int, int, int]:
    """returns (strength_moves, sets, cardio_min)"""
    cfg = {
        "Low": (3, 2, 15),
        "Medium": (4, 3, 25),
        "High": (5, 4, 35),
    }
    return cfg.get(intensity, (4,3,25))

def make_day(strength_moves: int, sets: int, cardio_min: int) -> List[ExerciseItem]:
    strength = random.sample(BANK["strength"], strength_moves)
    items: List[ExerciseItem] = [{"name": mv, "sets": sets, "reps": 8, "completed": False} for mv in strength]
    items.append({"name": random.choice(BANK["cardio"]), "minutes": cardio_min, "completed": False})
    return items

def generate_plan_for_user(user: User, days: int = 28, source: str = "AI",
                           goal: Literal["Weight Loss","Muscle Gain","Endurance"]="Weight Loss") -> WorkoutPlan:
    intensity = intensity_from_profile(user, goal) if source == "AI" else "Medium"

    strength_moves, sets, cardio = preset_volume(intensity)
    start = date.today()

    plan = WorkoutPlan(user_id=user.id, start_date=start, days=days, source=source, intensity=intensity)
    db.session.add(plan)
    db.session.flush()  # get plan.id

    for i in range(days):
        d = start + timedelta(days=i)
        # 3 on, 1 off pattern
        if (i % 4) == 3:
            items = [{"name": "Active recovery walk", "minutes": 20, "completed": False}]
        else:
            items = make_day(strength_moves, sets, cardio)
        db.session.add(WorkoutDay(plan_id=plan.id, day_index=i, date=d, items=items))

    db.session.commit()
    return plan

def get_today_for_user(user: User) -> Tuple[WorkoutPlan | None, WorkoutDay | None, int | None]:
    plan = (WorkoutPlan.query
            .filter_by(user_id=user.id)
            .order_by(WorkoutPlan.start_date.desc())
            .first())
    if not plan: return None, None, None
    delta = (date.today() - plan.start_date).days
    if delta < 0 or delta >= plan.days: return plan, None, delta
    wday = WorkoutDay.query.filter_by(plan_id=plan.id, day_index=delta).first()
    return plan, wday, delta
