from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.book_service import get_book_by_id, insert_book, update_book

book_bp = Blueprint('book', __name__, url_prefix='/books')

@book_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        published_year = request.form.get('published_year')
        image_url = request.form.get('image_url')

        if not title or not author:
            flash('Title and author are required.', 'danger')
            return redirect(request.url)

        book_data = {
            'user_id': session['user_id'],
            'title': title,
            'author': author,
            'genre': genre,
            'published_year': published_year,
            'image_url': image_url
        }

        insert_book(book_data)
        flash('Book created successfully!', 'success')
        return redirect(url_for('home.index'))

    return render_template('books/book-form.html', action='create', book=None)

@book_bp.route('/<int:book_id>/update', methods=['GET', 'POST'])
def update(book_id):
    book = get_book_by_id(book_id, session['user_id'])
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        published_year = request.form.get('published_year')
        image_url = request.form.get('image_url')

        if not title or not author:
            flash('Title and author are required.', 'danger')
            return redirect(request.url)

        book_data = {
            'id': book_id,
            'user_id': session['user_id'],
            'title': title,
            'author': author,
            'genre': genre,
            'published_year': published_year,
            'image_url': image_url
        }

        update_book(book_data)
        flash('Book updated successfully!', 'success')
        return redirect(url_for('home.index'))

    return render_template('books/book-form.html', action='update', book=book)