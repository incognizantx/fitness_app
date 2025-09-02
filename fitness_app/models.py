from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from fitness_app.extensions import db, login_manager
from fitness_app import db
from sqlalchemy import JSON, UniqueConstraint
from sqlalchemy.ext.mutable import MutableList
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    gender = db.Column(db.String(10))  # "Male" / "Female"
    fitness_level = db.Column(db.String(20), default="Intermediate")  # "Beginner", "Intermediate", "Advanced"
    previous_success_rate = db.Column(db.Float, default=0.7)
    previous_goal = db.Column(db.String(20), default="Weight Loss")   # "Weight Loss", "Muscle Gain", "Endurance"
    user_rating = db.Column(db.Float, default=4.0)
    plan_adherence_rate = db.Column(db.Float, default=0.8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bmi = db.Column(db.Float)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
class WorkoutPlan(db.Model):
    """One active plan per user at a time."""
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, default="Weight Loss")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, default=date.today, index=True)
    days = db.Column(db.Integer, default=28)                # 4 weeks by default
    source = db.Column(db.String(20), default="AI")         # "AI" or "Preset"
    intensity = db.Column(db.String(10))                    # Low/Medium/High (from AI)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("plans", lazy=True))

class WorkoutDay(db.Model):
    """Stores the plan for a specific calendar day as a JSON list of items."""
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("workout_plan.id"), nullable=False, index=True)
    day_index = db.Column(db.Integer, nullable=False)  # 0..N-1 within plan
    date = db.Column(db.Date, nullable=False, index=True)
    items = db.Column(MutableList.as_mutable(db.JSON), nullable=False)           # [{name, sets, reps, minutes, completed}]
    # ensure one record per plan/day_index
    __table_args__ = (UniqueConstraint('plan_id', 'day_index', name='uq_plan_day'),)

    plan = db.relationship("WorkoutPlan", backref=db.backref("days_list", lazy=True, order_by="WorkoutDay.day_index"))

class WorkoutLog(db.Model):
    """Optional detailed log per completed item (checkbox events, notes)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    workout_day_id = db.Column(db.Integer, db.ForeignKey("workout_day.id"), index=True)
    item_index = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    user = db.relationship("User")
    day = db.relationship("WorkoutDay")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
