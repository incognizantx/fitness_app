from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from fitness_app.models import User, db, WorkoutPlan, WorkoutDay, WorkoutLog
from fitness_app.forms import WorkoutPlanForm
from fitness_app.planner import generate_plan_for_user, get_today_for_user
from datetime import date

main_bp = Blueprint("main", __name__, url_prefix="")

@main_bp.route("/")
def index():
    return render_template("main/dashboard.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    todays_plan = WorkoutPlan.query.filter_by(
        user_id=current_user.id,
        created_at=date.today()
    ).first()

    return render_template(
        "main/dashboard.html",
        user=current_user,
        today=todays_plan
    )

@main_bp.route("/admin")
@login_required
def admin_dashboard():
    users = User.query.all()
    if not current_user.is_admin:  
        # Non-admins → show access denied page
        return render_template("access_denied.html"), 403

    return render_template("admin_dashboard.html", users=users)

@main_bp.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    form = WorkoutPlanForm()   # ✅ create form instance
    if form.validate_on_submit():
        plan = WorkoutPlan(
            source=form.source.data,
            goal=form.goal.data,
            days=form.days.data,
            user_id=current_user.id,
        )

    #         id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    # start_date = db.Column(db.Date, default=date.today, index=True)
    # days = db.Column(db.Integer, default=28)                # 4 weeks by default
    # source = db.Column(db.String(20), default="AI")         # "AI" or "Preset"
    # intensity = db.Column(db.String(10))                    # Low/Medium/High (from AI)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
        db.session.add(plan)
        db.session.commit()
        flash("Workout plan created!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("main/planner.html", form=form)  # ✅ pass form

@main_bp.route("/toggle_item", methods=["POST"])
@login_required
def toggle_item():
    """AJAX: toggle completion for an item in today's workout."""
    day_id = int(request.form["day_id"])
    idx = int(request.form["item_index"])
    day = WorkoutDay.query.get_or_404(day_id)
    if day.plan.user_id != current_user.id:
        return jsonify({"ok": False, "error": "Forbidden"}), 403

    items = day.items or []
    if idx < 0 or idx >= len(items):
        return jsonify({"ok": False, "error": "Bad index"}), 400

    items[idx]["completed"] = not bool(items[idx].get("completed"))
    day.items = items
    db.session.add(day)
    db.session.add(WorkoutLog(user_id=current_user.id, workout_day_id=day.id, item_index=idx,
                              completed=items[idx]["completed"]))
    db.session.commit()
    return jsonify({"ok": True, "completed": items[idx]["completed"]})