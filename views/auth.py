from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import register_user, authenticate

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate(username, password)
        if not user:
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["id"]
        return redirect(url_for("home.index"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        register_user(username, password)

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")
