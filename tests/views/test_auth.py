"""Tests for authentication views."""
import pytest


class TestLoginView:
    """Test login functionality."""

    def test_login_get_renders_page(self, app_client):
        """Test that GET /login renders the login form."""
        response = app_client.get("/login")
        
        assert response.status_code == 200
        assert b"login" in response.data.lower()

    def test_login_success_with_valid_credentials(self, app_client, test_user):
        """Test successful login with valid credentials."""
        response = app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # Should redirect to home page
        assert b"home" in response.data.lower() or response.request.path == "/"

    def test_login_success_sets_session(self, app_client, test_user):
        """Test that successful login sets session variables."""
        response = app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"},
            follow_redirects=False
        )
        
        # Use session_transaction to inspect session
        with app_client.session_transaction() as sess:
            assert "user_id" in sess
            assert "user" in sess
            assert sess["user"] == "testuser"
            assert sess["user_id"] == test_user["id"]

    def test_login_failure_wrong_password(self, app_client, test_user):
        """Test login fails with wrong password."""
        response = app_client.post(
            "/login",
            data={"username": "testuser", "password": "wrong_password"},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"invalid" in response.data.lower()

    def test_login_failure_missing_username(self, app_client):
        """Test login fails when username is missing."""
        response = app_client.post(
            "/login",
            data={"password": "some_password"},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_login_failure_missing_password(self, app_client):
        """Test login fails when password is missing."""
        response = app_client.post(
            "/login",
            data={"username": "testuser"},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_login_success_prevents_session_fixation(self, app_client, test_user):
        """Test that successful login clears session first (prevents fixation)."""
        # Set an initial session value
        with app_client.session_transaction() as sess:
            sess["old_value"] = "should_be_cleared"
        
        # Login
        app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"}
        )
        
        # Old session value should be cleared
        with app_client.session_transaction() as sess:
            assert "old_value" not in sess
            assert "user" in sess


class TestRegisterView:
    """Test registration functionality."""

    def test_register_get_renders_page(self, app_client):
        """Test that GET /register renders the registration form."""
        response = app_client.get("/register")
        
        assert response.status_code == 200
        assert b"register" in response.data.lower()

    def test_register_success_with_valid_data(self, app_client):
        """Test successful registration with valid credentials."""
        response = app_client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "SecurePass123",
                "confirmPassword": "SecurePass123"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"success" in response.data.lower() or b"login" in response.data.lower()

    def test_register_failure_duplicate_username(self, app_client, test_user):
        """Test registration fails with duplicate username."""
        response = app_client.post(
            "/register",
            data={
                "username": "testuser",
                "password": "password",
                "confirmPassword": "password"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"taken" in response.data.lower()

    def test_register_failure_passwords_dont_match(self, app_client):
        """Test registration fails when passwords don't match."""
        response = app_client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "Password123",
                "confirmPassword": "DifferentPass123"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"match" in response.data.lower()

    def test_register_failure_missing_fields(self, app_client):
        """Test registration fails when required fields are missing."""
        response = app_client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "password"
                # confirmPassword missing
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b"required" in response.data.lower() or b"fill" in response.data.lower()

    def test_register_failure_empty_username(self, app_client):
        """Test registration fails with empty username."""
        response = app_client.post(
            "/register",
            data={
                "username": "",
                "password": "password",
                "confirmPassword": "password"
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # Should show error message
        assert response.request.path == "/register" or b"required" in response.data.lower()


class TestLogoutView:
    """Test logout functionality."""

    def test_logout_clears_session(self, app_client, test_user):
        """Test that logout clears the session."""
        # First login
        app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"}
        )
        with app_client.session_transaction() as sess:
            assert "user" in sess
        
        # Then logout
        app_client.get("/logout")
        
        # Session should be cleared
        with app_client.session_transaction() as sess:
            assert "user" not in sess
            assert "user_id" not in sess

    def test_logout_redirects_to_home(self, app_client, test_user):
        """Test that logout redirects to home page."""
        # First login
        app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"}
        )
        
        # Then logout
        response = app_client.get("/logout", follow_redirects=False)
        
        assert response.status_code == 302  # Redirect status
        assert "/" in response.location

    def test_logout_shows_message(self, app_client, test_user):
        """Test that logout shows a flash message."""
        # First login
        app_client.post(
            "/login",
            data={"username": "testuser", "password": "test_password"}
        )
        
        # Then logout and follow redirect
        response = app_client.get("/logout", follow_redirects=True)
        
        assert b"logged out" in response.data.lower()


class TestAuthenticationFlow:
    """Test complete authentication workflows."""

    def test_full_auth_flow_register_login_logout(self, app_client):
        """Test complete flow: register -> login -> logout."""
        # Register
        register_response = app_client.post(
            "/register",
            data={
                "username": "newuser",
                "password": "SecurePass123",
                "confirmPassword": "SecurePass123"
            },
            follow_redirects=True
        )
        assert register_response.status_code == 200
        
        # Login with new credentials
        login_response = app_client.post(
            "/login",
            data={"username": "newuser", "password": "SecurePass123"},
            follow_redirects=True
        )
        assert login_response.status_code == 200
        
        # Logout
        logout_response = app_client.get("/logout", follow_redirects=True)
        assert logout_response.status_code == 200
        assert b"logged out" in logout_response.data.lower()

    def test_protected_routes_require_login(self, app_client):
        """Test that protected routes redirect to login if not authenticated."""
        # Try to access home without login
        response = app_client.get("/", follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert "/login" in response.location

    @pytest.mark.parametrize("route", [
        "/",
        "/books/create",
        "/quotes/",
        "/quotes/create",
    ])
    def test_protected_routes_redirect_to_login(self, app_client, route):
        """Test that various protected routes redirect to login."""
        response = app_client.get(route, follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login" in response.location

    @pytest.mark.parametrize("missing_field,expected_message", [
        ("username", b"required"),
        ("password", b"required"),
    ])
    def test_login_failure_missing_fields_parametrized(self, app_client, missing_field, expected_message):
        """Parametrized test for login with missing required fields."""
        data = {"password": "some_password"} if missing_field == "username" else {"username": "testuser"}
        
        response = app_client.post("/login", data=data, follow_redirects=True)
        
        assert response.status_code == 200
        assert expected_message in response.data.lower()

    @pytest.mark.parametrize("username,password,should_succeed,expected_message", [
        ("testuser", "test_password", True, b"home"),
        ("testuser", "wrong_password", False, b"invalid"),
        ("nonexistent", "anypassword", False, b"invalid"),
        ("", "password", False, b"required"),
        ("testuser", "", False, b"required"),
    ])
    def test_login_scenarios_parametrized(self, app_client, test_user, username, password, should_succeed, expected_message):
        """Parametrized test for various login scenarios."""
        response = app_client.post("/login", data={"username": username, "password": password}, follow_redirects=True)
        
        assert response.status_code == 200
        if should_succeed:
            assert expected_message in response.data.lower() or response.request.path == "/"
        else:
            assert expected_message in response.data.lower()
