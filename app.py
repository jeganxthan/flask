from flask import Flask
from flask_cors import CORS
from db import db
from extensions import mail
from controllers.notes_controller import notes_bp
from controllers.auth_controller import auth_bp
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()

    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'notes.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    # Mail Config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

    db.init_app(app)
    mail.init_app(app)
    CORS(app)
    JWTManager(app)

    app.register_blueprint(notes_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
