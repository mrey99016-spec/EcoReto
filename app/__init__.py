from flask import Flask
from .config import Config
from .db import init_db, close_db
from .routes import bp

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    app.register_blueprint(bp)
    return app

app = create_app()
