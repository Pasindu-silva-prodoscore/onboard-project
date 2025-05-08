from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    from .config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .routes.pins import pins_bp
    from .routes.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/v1')
    app.register_blueprint(pins_bp, url_prefix='/api/v1')
    
    from .utils.errors import register_error_handlers
    register_error_handlers(app)
    
    return app