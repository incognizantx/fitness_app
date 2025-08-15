from flask import Flask, render_template, request
import random

app = Flask(__name__)

EXERCISES = {
    "Weight Loss": [
        "30 min brisk walking", "20 min HIIT cardio", "Cycling - 10 km",
        "Jump rope - 10 min", "Swimming - 30 min", "Bodyweight circuit training"
    ],
    "Muscle Gain": [
        "Bench press - 4 sets", "Deadlift - 4 sets", "Squats - 4 sets",
        "Overhead press - 4 sets", "Pull-ups - 3 sets", "Dumbbell curls - 3 sets"
    ],
    "Endurance": [
        "5 km run", "Cycling - 15 km", "Rowing machine - 20 min",
        "Swimming - 40 min", "Stair climbing - 20 min", "Burpees - 3 sets"
    ]
}

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    weight = float(request.form["weight"])
    height = float(request.form["height"])
    age = int(request.form["age"])
    gender = request.form["gender"]
    goal = request.form["goal"]
    duration = request.form["duration"]

    base_exercises = EXERCISES.get(goal, [])
    if duration == "Day":
        plan = random.sample(base_exercises, min(3, len(base_exercises)))
    elif duration == "Week":
        plan = [f"Day {i+1}: " + ", ".join(random.sample(base_exercises, 3)) for i in range(7)]
    elif duration == "Month":
        plan = [f"Week {i+1}: " + ", ".join(random.sample(base_exercises, 4)) for i in range(4)]
    else:
        plan = []

    return render_template("results.html", plan=plan, duration=duration)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
