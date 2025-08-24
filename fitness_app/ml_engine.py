import os
import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

MODEL_PATH_INTENSITY = "model_intensity.joblib"
MODEL_PATH_PLAN_SUCCESS = "model_plan_success.joblib"

# Goals in a fixed order so we can one-hot properly
GOALS = ["Weight Loss", "Muscle Gain", "Endurance"]
GENDERS = ["Male", "Female"]

FEATURE_COLS = [
    "age", "gender", "height_cm", "weight_kg", "BMI", "fitness_level", "goal",
    "plan_length_days", "avg_intensity", "avg_sets_per_day", "avg_reps_per_set",
    "avg_cardio_minutes_per_day", "exercise_types_count", "previous_success_rate",
    "previous_goal", "plan_adherence_rate", "user_rating"
]

# 1. Load and preprocess your real dataset
def load_dataset(csv_path="fitness_dataset.csv"):
    # Always resolve path relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, csv_path)
    df = pd.read_csv(csv_path)
    # Encode gender: 0 for Female, 1 for Male
    df["gender"] = df["gender"].map({"Female": 0, "Male": 1})
    # Encode fitness_level: e.g., Beginner=0, Intermediate=1, Advanced=2
    df["fitness_level"] = df["fitness_level"].map({"Beginner": 0, "Intermediate": 1, "Advanced": 2})
    # Encode goal: e.g., Weight Loss=0, Muscle Gain=1, Endurance=2
    df["goal"] = df["goal"].map({"Weight Loss": 0, "Muscle Gain": 1, "Endurance": 2})
    # Encode previous_goal similarly
    df["previous_goal"] = df["previous_goal"].map({"Weight Loss": 0, "Muscle Gain": 1, "Endurance": 2})
    # If avg_intensity is categorical, encode it too
    if df["avg_intensity"].dtype == object:
        df["avg_intensity"] = df["avg_intensity"].map({"Low": 0, "Medium": 1, "High": 2})
    return df

def _make_synthetic_dataset(n=2000, seed=42):
    """
    We generate a simple synthetic dataset:
      X features: [age, BMI, gender_is_male, goal_wl, goal_mg, goal_end]
      y target: intensity_class in {0:Low, 1:Medium, 2:High}
    Target is created by heuristic + noise so the model learns a sensible rule.
    """
    rng = np.random.default_rng(seed)
    age = rng.integers(12, 81, size=n)                # 12..80
    bmi = rng.uniform(16, 40, size=n)                 # underweight..obese
    gender_male = rng.integers(0, 2, size=n)          # 0/1
    goal_idx = rng.integers(0, 3, size=n)             # 0..2

    goal_oh = np.zeros((n, 3), dtype=int)
    goal_oh[np.arange(n), goal_idx] = 1

    # Heuristic base score: higher for muscle gain & endurance, lower for high BMI & older age
    base = (
        0.6 * goal_oh[:, 1] +         # Muscle Gain tends higher intensity
        0.5 * goal_oh[:, 2] +         # Endurance medium-high
        0.3 * goal_oh[:, 0]           # Weight Loss medium
    )
    base += 0.25 * gender_male        # slight bump for male
    base -= 0.02 * np.clip(age - 35, 0, None)  # intensity reduces after ~35
    base -= 0.03 * np.clip(bmi - 27, 0, None)  # intensity reduces for BMI>27
    base += rng.normal(0, 0.15, size=n)        # noise

    # Map continuous base to classes
    # thresholds chosen to produce roughly balanced classes
    y = np.digitize(base, bins=[0.15, 0.55])   # 0:low, 1:med, 2:high

    X = np.column_stack([age, bmi, gender_male, goal_oh])
    return X, y

# 2. Train and save the model
def train_and_save_model(csv_path="fitness_dataset.csv"):
    df = load_dataset(csv_path)
    X = df[FEATURE_COLS]
    y = df["plan_success"]
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X, y)
    dump(clf, MODEL_PATH_PLAN_SUCCESS)
    return clf

# 3. Load the model (train if missing)
def ensure_model():
    if os.path.exists(MODEL_PATH_PLAN_SUCCESS):
        try:
            return load(MODEL_PATH_PLAN_SUCCESS)
        except Exception:
            pass
    return train_and_save_model()

_model = ensure_model()

# 4. Featurize a user/plan for prediction
def featurize_user_plan(user, plan_params):
    """
    user: dict with user features (expects 'gender' as 0 or 1)
    plan_params: dict with plan features
    Returns: np.array of features in the same order as training
    """
    features = [
        user["age"],
        user["gender"],  # 0 for Female, 1 for Male
        user["height_cm"],
        user["weight_kg"],
        user["BMI"],
        user["fitness_level"],
        plan_params["goal"],
        plan_params["plan_length_days"],
        plan_params["avg_intensity"],
        plan_params["avg_sets_per_day"],
        plan_params["avg_reps_per_set"],
        plan_params["avg_cardio_minutes_per_day"],
        plan_params["exercise_types_count"],
        plan_params["previous_success_rate"],
        plan_params["previous_goal"],
        plan_params["plan_adherence_rate"],
        plan_params["user_rating"]
    ]
    return np.array(features).reshape(1, -1)

# 5. Predict plan success
def predict_plan_success(user, plan_params):
    X = featurize_user_plan(user, plan_params)
    pred = int(_model.predict(X)[0])
    return pred  # 1 = likely success, 0 = likely not

# 6. (Optional) Suggest best plan from candidates
def suggest_best_plan(user, plan_candidates):
    """
    plan_candidates: list of plan_params dicts
    Returns: plan_params dict with highest predicted success
    """
    best_plan = None
    best_score = -1
    for plan in plan_candidates:
        score = predict_plan_success(user, plan)
        if score > best_score:
            best_score = score
            best_plan = plan
    print(f"Yes, it is ML! Plan with predicted success: {best_score}")
    return best_plan

def _featurize(age: int, weight_kg: float, height_cm: float, gender: str, goal: str):
    h_m = height_cm / 100.0
    bmi = weight_kg / (h_m * h_m) if h_m > 0 else 0.0
    gender_male = 1 if gender == "Male" else 0
    goal_vec = [1 if goal == g else 0 for g in GOALS]
    X = np.array([age, bmi, gender_male] + goal_vec, dtype=float).reshape(1, -1)
    return X, bmi

def predict_intensity(age, weight_kg, height_cm, gender, goal):
    """
    Returns: (intensity_label, bmi_value)
      intensity_label in {"Low","Medium","High"}
    """
    X, bmi = _featurize(age, weight_kg, height_cm, gender, goal)
    pred = int(_model.predict(X)[0])
    label = ["Low", "Medium", "High"][pred]
    print(label)
    return label, float(bmi)

# Example usage:
# user = {"age": 28, "gender_Male": 1, "gender_Female": 0}
# plan = {"goal_WL": 1, "goal_MG": 0, "goal_End": 0, ...}
# result = predict_plan_success(user, plan)


