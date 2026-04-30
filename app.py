import os
import logging
import logging.handlers
from flask import Flask, request, session, redirect, url_for
from views import home_bp, auth_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# Configure logging to file with daily rotation
log_filename = "app.log"
handler = logging.handlers.TimedRotatingFileHandler(
    log_filename, when="midnight", interval=1, backupCount=30
)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@app.before_request
def log_request():
    logging.info(f"Request: {request.method} {request.url} from {request.remote_addr}")


@app.before_request
def require_login():
    if (
        not session.get("user")
        and request.endpoint not in ["auth.login", "auth.register"]
        and not request.path.startswith("/static/")
    ):
        return redirect(url_for("auth.login"))


app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
