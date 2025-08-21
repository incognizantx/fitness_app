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
    plan, today, delta = get_today_for_user(current_user)
    return render_template(
        "main/dashboard.html",
        user=current_user,
        plan=plan,
        today=today,
        day_index=delta
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
        # Use the generator to create plan and days
        generate_plan_for_user(
            current_user,
            days=form.days.data,
            source=form.source.data,
            goal=form.goal.data
        )
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