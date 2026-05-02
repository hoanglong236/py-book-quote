import pytest
import sqlite3
import os
import tempfile
from app import app


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # Override DATABASE in both modules BEFORE calling init_db
    import database.db
    import database.schema
    
    original_db_module = database.db.DATABASE
    original_schema = database.schema.DATABASE
    
    database.db.DATABASE = db_path
    database.schema.DATABASE = db_path
    
    # Initialize the test database with the correct path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        published_year INTEGER NOT NULL,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quote_text TEXT NOT NULL,
        author TEXT NOT NULL,
        favorite BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    )
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup: close the file and remove the database
    os.close(db_fd)
    os.unlink(db_path)
    
    # Restore original database paths
    database.db.DATABASE = original_db_module
    database.schema.DATABASE = original_schema


@pytest.fixture
def app_client(test_db):
    """Create a Flask test client with test database."""
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def db_connection(test_db):
    """Get a database connection for test setup/assertions."""
    from database import get_connection
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture
def test_user(db_connection):
    """Create a test user in the database."""
    from werkzeug.security import generate_password_hash
    
    cursor = db_connection.cursor()
    hashed_password = generate_password_hash("test_password")
    
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("testuser", hashed_password)
    )
    db_connection.commit()
    
    # Fetch and return the created user
    cursor.execute("SELECT id, username FROM users WHERE username = ?", ("testuser",))
    user = cursor.fetchone()
    return dict(user)
