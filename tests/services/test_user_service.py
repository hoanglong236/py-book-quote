"""Tests for authentication service functions."""
import pytest
from werkzeug.security import check_password_hash
from services import register_user, authenticate


class TestRegisterUser:
    """Test user registration logic."""

    def test_register_user_success(self, db_connection):
        """Test successful user registration with valid credentials."""
        result = register_user("newuser", "secure_password")
        
        assert result is True
        
        # Verify user was inserted into database
        cursor = db_connection.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", ("newuser",))
        user = cursor.fetchone()
        assert user is not None
        assert user["username"] == "newuser"

    def test_register_user_password_hashed(self, db_connection):
        """Test that passwords are hashed, not stored in plaintext."""
        password = "test_password_123"
        register_user("hashtest", password)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", ("hashtest",))
        user = cursor.fetchone()
        
        # Password should be hashed, not plaintext
        assert user["password"] != password
        # Hash should be verifiable
        assert check_password_hash(user["password"], password)

    def test_register_user_duplicate_username(self):
        """Test that duplicate usernames are rejected."""
        register_user("duplicate_user", "password1")
        result = register_user("duplicate_user", "password2")
        
        assert result is False

    def test_register_user_empty_username(self, db_connection):
        """Test that empty username is rejected."""
        result = register_user("", "password")
        
        assert result is False
        
        # Verify no user was created
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", ("",))
        count = cursor.fetchone()["count"]
        assert count == 0

    def test_register_user_empty_password(self, db_connection):
        """Test that empty password is rejected."""
        result = register_user("validuser_no_pass", "")
        
        assert result is False
        
        # Verify no user was created
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", ("validuser_no_pass",))
        count = cursor.fetchone()["count"]
        assert count == 0


class TestAuthenticate:
    """Test user authentication logic."""

    def test_authenticate_success(self, test_user):
        """Test successful authentication with correct credentials."""
        user = authenticate(test_user["username"], "test_password")
        
        assert user is not None
        assert user["username"] == test_user["username"]
        assert user["id"] == test_user["id"]

    def test_authenticate_wrong_password(self, test_user):
        """Test authentication fails with wrong password."""
        user = authenticate(test_user["username"], "wrong_password")
        
        assert user is None

    def test_authenticate_nonexistent_user(self):
        """Test authentication fails for non-existent user."""
        user = authenticate("nonexistent", "any_password")
        
        assert user is None

    def test_authenticate_returns_user_data(self, test_user):
        """Test that authenticate returns user id and username (not password)."""
        user = authenticate(test_user["username"], "test_password")
        
        assert user is not None
        assert "id" in user
        assert "username" in user
        # Should not return password hash
        assert "password" not in user or user.get("password") is None

    def test_authenticate_case_sensitive_username(self):
        """Test that username authentication is case-sensitive."""
        register_user("CaseSensitive", "password")
        
        # Test exact match
        user = authenticate("CaseSensitive", "password")
        assert user is not None
        
        # Test different case - should fail (case-sensitive)
        user_lower = authenticate("casesensitive", "password")
        assert user_lower is None
        
        # Test uppercase - should fail
        user_upper = authenticate("CASESENSITIVE", "password")
        assert user_upper is None

    def test_authenticate_empty_credentials(self):
        """Test authentication with empty credentials."""
        # Empty username
        user = authenticate("", "password")
        assert user is None
        
        # Empty password
        user = authenticate("testuser", "")
        assert user is None
        
        # Both empty
        user = authenticate("", "")
        assert user is None

    def test_authenticate_parametrized_simple(self):
        """Simple test for authentication success case."""
        # Create a user with unique username
        import time
        unique_username = f"validuser_{int(time.time())}"
        result = register_user(unique_username, "validpass")
        assert result is True
        
        # Try to authenticate
        user = authenticate(unique_username, "validpass")
        assert user is not None
        assert user["username"] == unique_username
