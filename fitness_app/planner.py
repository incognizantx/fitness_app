from datetime import date, timedelta
import random
from typing import List, Dict, Tuple, Literal
from fitness_app.models import WorkoutPlan, WorkoutDay, db, User
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os



# --- Exercise banks ---
BANKS = {
    "Weight Loss": {
        "strength": [
            "Goblet squats", "Walking lunges", "Kettlebell swings", "Plank", "Dips",
            "Push-ups", "Mountain climbers", "Bodyweight squats", "Step-ups", "Burpees",
            "Russian twists", "Jumping jacks", "Side lunges"
        ],
        "cardio": [
            "Incline walk", "Steady run", "Tempo run", "Cycling", "Elliptical",
            "Stair climber", "Swim", "Jump rope", "Rowing machine"
        ]
    },
    "Muscle Gain": {
        "strength": [
            "Back squats", "Front squats", "Romanian deadlifts", "Deadlifts",
            "Bench press", "Overhead press", "Barbell rows", "Pull-ups",
            "Dumbbell curls", "Tricep extensions", "Chest fly", "Lat pulldown",
            "Leg press", "Weighted dips", "Bulgarian split squats", "Hammer curls"
        ],
        "cardio": [
            "Rower easy", "Cycling", "Elliptical", "Farmer's walk", "Sled push"
        ]
    },
    "Endurance": {
        "strength": [
            "Plank", "Walking lunges", "Goblet squats", "Kettlebell swings",
            "Step-ups", "Push-ups", "Supermans", "Bodyweight squats",
            "Side lunges", "Mountain climbers", "Jumping jacks"
        ],
        "cardio": [
            "Steady run", "Tempo run", "Cycling", "Swim", "Incline walk",
            "Rowing machine", "Stair climber", "Jump rope"
        ]
    }
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
    "Swim": "https://www.swimnow.co.uk/wp-content/uploads/2023/05/Health-Benefits-of-Swimming.jpg",
    "Push-ups": "https://www.youtube.com/embed/WDIpL0pjun0?si=ZOHslrfgjZjlMWGU",
    "Mountain climbers": "https://www.youtube.com/embed/cnyTQDSE884?si=1JmX4f0kHfY4bX8G",
    "Bodyweight squats": "https://www.youtube.com/embed/aclHkVaku9U",
    "Step-ups": "https://www.youtube.com/embed/URHdW9js6DM",
    "Burpees": "https://www.youtube.com/embed/OO7-dWIy0W8",
    "Russian twists": "https://www.youtube.com/embed/wkD8rjkodUI",
    "Jumping jacks": "https://www.youtube.com/embed/uLVt6u15L98",
    "Side lunges": "https://www.youtube.com/embed/0R9ZQd3aM6s",
    "Jump rope": "https://www.youtube.com/embed/u3zgHI8QnqE",
    "Dumbbell curls": "https://www.youtube.com/embed/CFBZ4jN1CMI",
    "Tricep extensions": "https://www.youtube.com/embed/kZ-ReOdn2qk",
    "Chest fly": "https://www.youtube.com/embed/Nhvz9EzdJ4U",
    "Lat pulldown": "https://www.youtube.com/embed/NAIEnMjN-6w",
    "Leg press": "https://www.youtube.com/embed/cDGOn-yfKJA",
    "Weighted dips": "https://www.youtube.com/embed/MhPl9Vf4toc",
    "Bulgarian split squats": "https://www.youtube.com/embed/2C-uNgKwPLE",
    "Hammer curls": "https://www.youtube.com/embed/CFBZ4jN1CMI",
    "Farmer's walk": "https://www.youtube.com/embed/8OtwXwrJizk",
    "Sled push": "https://www.youtube.com/embed/QwscR2BhdEg"


}
def bmi_from_profile(u: User) -> float | None:
    return u.bmi

def preset_volume(intensity: str) -> Tuple[int, int, int]:
    """returns (strength_moves, sets, cardio_min)"""
    cfg = {
        "Low": (3, 2, 15),
        "Medium": (4, 3, 25),
        "High": (5, 4, 35),
    }
    return cfg.get(intensity)

def make_day(strength_moves: int, sets: int, cardio_min: int, bank) -> List[dict]:
    strength = random.sample(bank["strength"], min(strength_moves, len(bank["strength"])))
    items: List[dict] = [{"name": mv, "sets": sets, "reps": 8, "completed": False} for mv in strength]
    items.append({"name": random.choice(bank["cardio"]), "minutes": cardio_min, "completed": False})
    return items

def generate_plan_for_user(user: User, days: int = 28, source: str = "AI", goal: Literal["Weight Loss", "Muscle Gain", "Endurance"] = "Weight Loss"
) -> WorkoutPlan:
    bmi = bmi_from_profile(user)
    intensity = predict_intensity_from_bmi(bmi) if bmi is not None else 1
    strength_moves, sets, cardio = preset_volume(intensity)
    start = date.today()
    plan = WorkoutPlan(user_id=user.id, start_date=start, days=days, source=source, intensity=intensity, goal=goal)
    db.session.add(plan)
    db.session.flush()
    for i in range(days):
        d = start + timedelta(days=i)
        if (i % 4) == 3:
            items = [{"name": "Active recovery walk", "minutes": 20, "completed": False}]
        else:
            items = make_day(strength_moves, sets, cardio, BANKS[goal])
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

DTREE_PATH = os.path.join(os.path.dirname(__file__), "model_intensity.joblib")

def train_intensity_model():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "fitness_dataset.csv"))
    X = df[["BMI"]]
    y = df["avg_intensity"]
    clf = DecisionTreeClassifier(max_depth=3)
    clf.fit(X, y)
    joblib.dump(clf, DTREE_PATH)
    return clf

def get_intensity_model():
    if not os.path.exists(DTREE_PATH):
        return train_intensity_model()
    return joblib.load(DTREE_PATH)

def predict_intensity_from_bmi(bmi: float) -> str:
    clf = get_intensity_model()
    pred = int(clf.predict([[bmi]])[0])
    return ["Low", "Medium", "High"][pred]

