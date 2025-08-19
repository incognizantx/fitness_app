from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField, BooleanField
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
    submit = SubmitField("Create account")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")
