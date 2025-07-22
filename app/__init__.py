from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ducting.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register all blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.project import project_bp
    from .routes.seed import seed_bp   # ✅ Added for dummy vendors

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(seed_bp)   # ✅ Register seed route

    return app
