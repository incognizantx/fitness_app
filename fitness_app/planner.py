from datetime import date, timedelta
import random
from typing import List, Dict, Tuple, Literal
from fitness_app.models import WorkoutPlan, WorkoutDay, db, User
from fitness_app.ml_engine import suggest_best_plan 


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
MEDIA_LINKS = {
    "Back squats": "https://www.youtube.com/embed/-bJIpOq-LWk",
    "Front squats": "https://www.youtube.com/embed/W9jJaI4cHJU",
    "Romanian deadlifts": "https://www.youtube.com/embed/2bmuYtv4HbQ",
    "Deadlifts": "https://www.youtube.com/embed/yPqv3ejnZvc?si=BW1YXRhzOT_9Miqk",
    "Bench press": "https://www.youtube.com/embed/4_QuyfOCI5U",
    "Overhead press": "https://www.youtube.com/embed/cGnhixvC8uA",
    "Barbell rows": "https://www.youtube.com/embed/bm0_q9bR_HA",
    "Pull-ups": "https://www.youtube.com/embed/9yVGh3XbJ34",
    "Dips": "https://www.youtube.com/embed/WVeZDBhZwLA",
    "Goblet squats": "https://www.youtube.com/embed/MWHIs0zxkCU",
    "Walking lunges": "https://www.youtube.com/embed/UInwcEa5BH4",
    "Kettlebell swings": "https://www.youtube.com/embed/r777bo9KuY4",
    "Plank": "https://www.youtube.com/embed/mwlp75MS6Rg",
    "Rower easy": "https://www.youtube.com/embed/0R9ZQd3aM6s",
    "Incline walk": "https://liftmanual.com/wp-content/uploads/2023/04/walking-on-incline-treadmill.jpg",
    "Steady run": "https://sunriserunco.com/wp-content/uploads/2021/09/Steady-State-Running-featured-image.jpg",
    "Tempo run": "https://i0.wp.com/post.healthline.com/wp-content/uploads/2020/01/Runner-training-on-running-track-1296x728-header-1296x728.jpg?w=1155&h=1528",
    "Cycling": "https://cdn.mos.cms.futurecdn.net/v2/t:139,l:0,cw:2700,ch:1518,q:80,w:2700/WXZQnTcQHyt2igzrwhNUyW.jpg",
    "Elliptical": "https://shop.lifefitness.com/cdn/shop/products/life-fitness-e5-adjustable-stride-elliptical-cross-trainer-woman-1000x1000.jpg?v=1748945400&width=1000",
    "Stair climber": "https://assets.clevelandclinic.org/transform/LargeFeatureImage/30ac4994-09bb-4ebd-b114-46d1af479237/stair-stepper-gym-1474835659-r",
    "Swim": "https://www.swimnow.co.uk/wp-content/uploads/2023/05/Health-Benefits-of-Swimming.jpg"
}
def bmi_from_profile(u: User) -> float | None:
    if not (u.height_cm and u.weight_kg):
        return None
    h = max(u.height_cm, 1) / 100.0
    return round(u.weight_kg / (h*h), 1)

def preset_volume(intensity: str) -> Tuple[int, int, int]:
    """returns (strength_moves, sets, cardio_min)"""
    cfg = {
        "Low": (3, 2, 15),
        "Medium": (4, 3, 25),
        "High": (5, 4, 35),
    }
    return cfg.get(intensity)

def make_day(strength_moves: int, sets: int, cardio_min: int) -> List[ExerciseItem]:
    strength = random.sample(BANK["strength"], strength_moves)
    items: List[ExerciseItem] = [{"name": mv, "sets": sets, "reps": 8, "completed": False} for mv in strength]
    items.append({"name": random.choice(BANK["cardio"]), "minutes": cardio_min, "completed": False})
    return items

def generate_plan_for_user(
    user: User,
    days: int = 28,
    source: str = "AI",
    goal: Literal["Weight Loss", "Muscle Gain", "Endurance"] = "Weight Loss",
    intensity: Literal["Low", "Medium", "High"] = "Medium"
) -> WorkoutPlan:
    # 1. Prepare user features for ML
    user_features = {
        "age": user.age,
        "gender": 1 if user.gender == "Male" else 0,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "BMI": bmi_from_profile(user),
        "fitness_level": {"Beginner": 0, "Intermediate": 1, "Advanced": 2}.get(getattr(user, "fitness_level", "Intermediate"), 1),
        "previous_success_rate": getattr(user, "previous_success_rate", 0.7),
        "previous_goal": {"Weight Loss": 0, "Muscle Gain": 1, "Endurance": 2}.get(getattr(user, "previous_goal", goal), 0)
    }

    # 2. Build a candidate plan only for the selected intensity
    intensity_val = {"Low": 0, "Medium": 1, "High": 2}[intensity]
    strength_moves, sets, cardio = preset_volume(intensity)
    plan_candidates = [{
        "goal": {"Weight Loss": 0, "Muscle Gain": 1, "Endurance": 2}[goal],
        "plan_length_days": days,
        "avg_intensity": intensity_val,
        "avg_sets_per_day": sets,
        "avg_reps_per_set": 8,
        "avg_cardio_minutes_per_day": cardio,
        "exercise_types_count": strength_moves,
        "previous_success_rate": user_features["previous_success_rate"],
        "previous_goal": user_features["previous_goal"],
        "plan_adherence_rate": 0.8,  # Placeholder or from user history
        "user_rating": 4.0           # Placeholder or from user history
    }]

    # 3. Use ML to select the best plan (from one candidate, but keeps interface consistent)
    best_plan_params = suggest_best_plan(user_features, plan_candidates)

    # 4. Use best plan parameters to generate the actual plan
    intensity_label = intensity  # already a string: "Low", "Medium", or "High"
    strength_moves = best_plan_params["exercise_types_count"]
    sets = best_plan_params["avg_sets_per_day"]
    cardio = best_plan_params["avg_cardio_minutes_per_day"]
    start = date.today()

    plan = WorkoutPlan(user_id=user.id, start_date=start, days=days, source=source, intensity=intensity_label)
    db.session.add(plan)
    db.session.flush()  # get plan.id

    for i in range(days):
        d = start + timedelta(days=i)
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
            .order_by(WorkoutPlan.id.desc())
            .first())
    if not plan: return None, None, None
    delta = (date.today() - plan.start_date).days
    if delta < 0 or delta >= plan.days: return plan, None, delta
    wday = WorkoutDay.query.filter_by(plan_id=plan.id, day_index=delta).first()
    return plan, wday, delta
