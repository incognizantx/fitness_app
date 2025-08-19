from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You don’t have permission to access this page.", "danger")
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)
    return wrapper
