from flask import Blueprint, render_template, session, redirect, url_for
from services.book_service import get_all_books

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    user_id = session.get("user_id")

    books = get_all_books(user_id)
    return render_template("home.html", books=books)
