from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from fitness_app.models import User, db, WorkoutPlan, WorkoutDay, WorkoutLog
from fitness_app.forms import WorkoutPlanForm, ProfileForm
from fitness_app.planner import generate_plan_for_user, get_today_for_user
from datetime import date
from sqlalchemy.orm.attributes import flag_modified
from fitness_app.planner import MEDIA_LINKS
main_bp = Blueprint("main", __name__, url_prefix="")
@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        updated = False
        if form.email.data and form.email.data != current_user.email:
            current_user.email = form.email.data
            updated = True
        if form.password.data:
            current_user.set_password(form.password.data)
            updated = True
        if form.age.data is not None:
            current_user.age = form.age.data
            updated = True
        if form.height_cm.data is not None:
            current_user.height_cm = form.height_cm.data
            updated = True
        if form.weight_kg.data is not None:
            current_user.weight_kg = form.weight_kg.data
            updated = True
        if updated:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        else:
            flash("No changes made.", "info")
        return redirect(url_for("main.profile"))
    return render_template("main/profile.html", form=form, user=current_user, bg_image="backgrounds/dashboard.jpg")

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    plan, today, delta = get_today_for_user(current_user)
    days = []
    if plan:
        days = (WorkoutDay.query
                .filter_by(plan_id=plan.id)
                .order_by(WorkoutDay.day_index)
                .all())
    return render_template(
        "main/dashboard.html",
        user=current_user,
        plan=plan,
        today=today,
        day_index=delta,
        days=days,
        media_links=MEDIA_LINKS,
        bg_image="backgrounds/dashboard.jpg"
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
            intensity=form.intensity.data or "Medium",
            user=current_user,
            days=form.days.data,
            goal=form.goal.data
        )
        flash("Workout plan created!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("main/planner.html", form=form, bg_image="backgrounds/planner.jpg")  # ✅ pass form

@main_bp.route('/toggle_item', methods=['POST'])
@login_required
def toggle_item():
    day_id = request.form.get('day_id')
    item_index = int(request.form.get('item_index'))
    day = WorkoutDay.query.get(day_id)
    if day and 0 <= item_index < len(day.items):
        items = day.items
        items[item_index]['completed'] = True
        day.items = items
        flag_modified(day, "items")  # <-- Add this line
        db.session.commit()
        all_completed = all(item.get('completed') for item in day.items)
        return jsonify(success=True, all_completed=all_completed)
    return jsonify(success=False), 400