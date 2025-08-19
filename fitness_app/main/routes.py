from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from fitness_app.models import User, db

main_bp = Blueprint("main", __name__, url_prefix="")

@main_bp.route("/")
def index():
    return render_template("main/dashboard.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("main/dashboard.html", user=current_user)

@main_bp.route("/admin")
@login_required
def admin_dashboard():
    users = User.query.all()
    if not current_user.is_admin:  
        # Non-admins → show access denied page
        return render_template("access_denied.html"), 403

    return render_template("admin_dashboard.html", users=users)
