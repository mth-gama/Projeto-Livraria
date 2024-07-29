from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    
    with app.app_context():
        from . import routes, models
        db.create_all()
        
        @login.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))
        
        return app