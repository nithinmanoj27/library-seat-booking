from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS   # 👈 add this
from models import db
from config import Config

socketio = SocketIO(cors_allowed_origins="*")
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    CORS(app)   # 👈 allow requests from frontend (port 8000)

    with app.app_context():
        db.create_all()

    from routes import bp
    app.register_blueprint(bp)
    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
