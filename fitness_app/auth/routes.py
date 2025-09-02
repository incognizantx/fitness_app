from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from fitness_app.extensions import db
from fitness_app.models import User
from fitness_app.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter((User.email == form.email.data) | (User.username == form.username.data)).first():
            flash("Username or email already exists.", "warning")
            return render_template("auth/register.html", form=form)

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            age=form.age.data,
            height_cm=form.height_cm.data,
            weight_kg=form.weight_kg.data,
            gender=form.gender.data or None,
            fitness_level=form.fitness_level.data or "Intermediate",
            previous_goal=form.previous_goal.data or "Weight Loss"
        )
        user.set_password(form.password.data)
        # Calculate BMI and store
        if user.height_cm and user.weight_kg:
            h_m = max(user.height_cm, 1.0) / 100.0
            user.bmi = round(user.weight_kg / (h_m * h_m), 1)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form, bg_image="backgrounds/register.jpg")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data
        password = form.password.data

        # Try to find user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid username/email or password.", "danger")
    return render_template('auth/login.html', form=form, bg_image="backgrounds/login.jpg")

@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
