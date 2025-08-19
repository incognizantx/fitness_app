from fitness_app import create_app, db
from fitness_app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=generate_password_hash("10v52bA14B"),
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
