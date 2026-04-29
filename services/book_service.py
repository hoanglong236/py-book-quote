from database import get_connection


def get_all_books(user_id):
    """Retrieve all books for a specific user.

    Args:
        user_id: The ID of the user whose books to retrieve.

    Returns:
        A list of all book records for the user.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM books WHERE user_id = :user_id"
    cursor.execute(sql, {"user_id": user_id})

    books = cursor.fetchall()

    conn.close()
    return books


def get_book_by_id(id, user_id):
    """Retrieve a single book by ID for a specific user.

    Args:
        id: The book ID to retrieve.
        user_id: The ID of the user who owns the book.

    Returns:
        The book record if found, otherwise None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM books WHERE id = :id AND user_id = :user_id"
    cursor.execute(sql, {"id": id, "user_id": user_id})

    book = cursor.fetchone()

    conn.close()
    return book


def insert_book(book_dict):
    """Insert a new book into the database.

    Args:
        book_dict: A dictionary containing book data with keys:
                   user_id, title, author, genre, published_year, image_url.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO books (
        user_id,
        title,
        author,
        genre,
        published_year,
        image_url
    )
    VALUES (
        :user_id,
        :title,
        :author,
        :genre,
        :published_year,
        :image_url
    )
    """

    cursor.execute(sql, book_dict)

    conn.commit()
    conn.close()


def update_book(book_dict):
    """Update an existing book in the database.

    Args:
        book_dict: A dictionary containing updated book data with keys:
                   id, user_id, title, author, genre, published_year, image_url.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    UPDATE books
    SET
        title = :title,
        author = :author,
        genre = :genre,
        published_year = :published_year,
        image_url = :image_url
    WHERE id = :id AND user_id = :user_id
    """

    cursor.execute(sql, book_dict)

    conn.commit()
    conn.close()


def delete_book(book_dict):
    """Delete a book from the database.

    Args:
        book_dict: A dictionary containing book_id and user_id for the book to delete.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM books WHERE id = :id AND user_id = :user_id"
    cursor.execute(sql, book_dict)

    conn.commit()
    conn.close()
