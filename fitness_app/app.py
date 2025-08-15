from flask import Flask, render_template, request
import random
from ml_engine import predict_intensity

app = Flask(__name__)

EXERCISES = {
    "Weight Loss": {
        "strength": ["Bodyweight squats", "Push-ups", "Walking lunges", "Dumbbell rows", "Plank holds", "Kettlebell swings"],
        "cardio":   ["Brisk walk", "HIIT intervals", "Cycling", "Elliptical", "Rowing", "Jump rope"]
    },
    "Muscle Gain": {
        "strength": ["Back squats", "Deadlifts", "Bench press", "Overhead press", "Barbell rows", "Pull-ups", "Dips", "Romanian deadlifts"],
        "cardio":   ["Incline walk", "Light cycling", "Rower easy pace"]
    },
    "Endurance": {
        "strength": ["Goblet squats", "Step-ups", "Kettlebell clean & press", "Walking lunges", "Core circuit", "Single-leg RDL"],
        "cardio":   ["Steady run", "Tempo run", "Long ride", "Rowing steady", "Stair climber", "Swim"]
    }
}
def generate_plan():
    return {
        "Week 1": [
            ["Back squats — 4 sets", "Romanian deadlifts — 4 sets", "Bench press — 4 sets", "Pull-ups — 4 sets", "Cardio: 35 min Rower (easy pace)"],
            ["Overhead press — 4 sets", "Dips — 4 sets", "Incline walk — 35 min"],
            ["Deadlifts — 4 sets", "Barbell rows — 4 sets", "Pull-ups — 4 sets", "Cardio: 35 min Incline walk"]
        ],
        "Week 2": [
            ["Deadlifts — 4 sets", "Barbell rows — 4 sets", "Dips — 4 sets", "Pull-ups — 4 sets", "Cardio: 35 min Incline walk"],
            ["Overhead press — 4 sets", "Bench press — 4 sets", "Rower — 35 min easy pace"],
            ["Romanian deadlifts — 4 sets", "Back squats — 4 sets", "Cardio: 35 min Incline walk"]
        ]
        # You can extend for Week 3, Week 4, etc.
    }


def build_plan(goal, duration, intensity):
    """
    intensity: 'Low' | 'Medium' | 'High'
    We scale total sets and cardio minutes by intensity and duration.
    """
    cfg = {
        "Low":    {"sets_per_strength_move": 2, "strength_moves": 4, "cardio_min": 15},
        "Medium": {"sets_per_strength_move": 3, "strength_moves": 5, "cardio_min": 25},
        "High":   {"sets_per_strength_move": 4, "strength_moves": 6, "cardio_min": 35},
    }[intensity]

    bank = EXERCISES[goal]
    strength_pool = bank["strength"]
    cardio_pool = bank["cardio"]

    def day_plan(day_idx=None):
        strength = random.sample(strength_pool, min(cfg["strength_moves"], len(strength_pool)))
        cardio = random.choice(cardio_pool)
        strength_text = ", ".join(f"{mv} — {cfg['sets_per_strength_move']} sets" for mv in strength)
        return f"{('Day ' + str(day_idx) + ': ') if day_idx else ''}{strength_text}; Cardio: {cfg['cardio_min']} min {cardio}"

    if duration == "Day":
        return [day_plan()]
    elif duration == "Week":
        return [day_plan(i+1) for i in range(7)]
    elif duration == "Month":
        # 4 weeks summary (each entry describes a representative week)
        return [f"Week {i+1}: " + ", ".join([day_plan() for _ in range(3)]) for i in range(4)]
    return []

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    weight = float(request.form["weight"])
    height = float(request.form["height"])
    age = int(request.form["age"])
    gender = request.form["gender"]            # "Male" | "Female"
    goal = request.form["goal"]                # in EXERCISES keys
    duration = request.form["duration"]        # Day | Week | Month

    intensity, bmi = predict_intensity(age, weight, height, gender, goal)
    plan = build_plan(goal, duration, intensity)

    # For transparency, show the calculated BMI and intensity
    summary = {
        "bmi": round(bmi, 1),
        "intensity": intensity,
        "goal": goal,
        "duration": duration,
        "gender": gender,
        "age": age,
        "weight": weight,
        "height": height
    }
    return render_template("results.html", plan=plan, duration=duration, summary=summary)

@app.route("/plan")
def plan():
    fitness_plan = generate_plan()
    return render_template("plan.html", fitness_plan=fitness_plan)
if __name__ == "__main__":
    # Expose to LAN so you can open on phone
    app.run(debug=True)
