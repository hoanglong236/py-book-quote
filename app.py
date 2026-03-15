import os
from flask import Flask
from views import home_bp, auth_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
