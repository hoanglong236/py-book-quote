from flask import Flask
from views import home_bp, about_bp

app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(about_bp)