from flask import Flask
from fitness_app.extensions import db, login_manager, csrf
from fitness_app.auth.routes import auth_bp
from fitness_app.main.routes import main_bp
import os

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Basic config (use env vars in prod)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///fitness.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Create DB (dev convenience)
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    # Expose to LAN for mobile testing
    app.run(host="0.0.0.0", port=5000, debug=True)
