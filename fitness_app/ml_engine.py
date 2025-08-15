import os
import numpy as np
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = "model_intensity.joblib"

# Goals in a fixed order so we can one-hot properly
GOALS = ["Weight Loss", "Muscle Gain", "Endurance"]
GENDERS = ["Male", "Female"]

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

def _train_and_save_model():
    X, y = _make_synthetic_dataset()
    clf = RandomForestClassifier(
        n_estimators=120, max_depth=6, random_state=7, class_weight="balanced"
    )
    clf.fit(X, y)
    dump(clf, MODEL_PATH)
    return clf

def _ensure_model():
    if os.path.exists(MODEL_PATH):
        try:
            return load(MODEL_PATH)
        except Exception:
            pass
    return _train_and_save_model()

_model = _ensure_model()

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
    return label, float(bmi)
