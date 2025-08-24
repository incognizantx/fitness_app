from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    age = IntegerField("Age", validators=[Optional(), NumberRange(12, 80)])
    height_cm = FloatField("Height (cm)", validators=[Optional(), NumberRange(100, 230)])
    weight_kg = FloatField("Weight (kg)", validators=[Optional(), NumberRange(30, 250)])
    gender = SelectField("Gender", choices=[("Male", "Male"), ("Female", "Female")], validators=[Optional()])
    fitness_level = SelectField("Fitness Level", choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], default="Intermediate", validators=[Optional()])
    previous_success_rate = FloatField("Previous Success Rate", validators=[Optional(), NumberRange(0.0, 1.0)])
    previous_goal = SelectField("Previous Goal", choices=[("Weight Loss", "Weight Loss"), ("Muscle Gain", "Muscle Gain"), ("Endurance", "Endurance")], default="Weight Loss", validators=[Optional()])
    user_rating = FloatField("User Rating", validators=[Optional(), NumberRange(1.0, 5.0)])
    
    
    
    submit = SubmitField("Create account")

class LoginForm(FlaskForm):
    identifier = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")
class WorkoutPlanForm(FlaskForm):
    intensity = SelectField("Intensity", choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")], default="Medium", validators=[Optional()])
    goal = StringField("Goal", validators=[Optional()])
    days = IntegerField("Duration", validators=[Optional(), NumberRange(1,56)])
    submit = SubmitField("Create Plan")