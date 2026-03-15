from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import register_user, authenticate

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required", "danger")
            return redirect(url_for("auth.login"))

        user = authenticate(username, password)

        if not user:
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))

        # prevent session fixation
        session.clear()
        session["user_id"] = user["id"]

        return redirect(url_for("home.index"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        if not username or not password or not confirm_password:
            flash("Please fill in all required fields")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("auth.register"))

        success = register_user(username, password)

        if not success:
            flash("This username is already taken")
            return redirect(url_for("auth.register"))

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")
