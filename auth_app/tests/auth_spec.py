# tests/auth.spec.py

import pytest
from rest_framework.test import APIClient
from auth_app.models import User


@pytest.mark.django_db
class TestAuthEndpoints:
    client = APIClient()

    # It Should Register User Successfully with Default Organisation.
    def test_register_user_successfully(self):
        response = self.client.post(
            "/auth/register",
            data={
                "email": "test@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "password": "password123",
                "phone":"09095209660"
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Registration successful"
        assert "accessToken" in data["data"]
        assert "refreshToken" in data["data"]
        assert data["data"]["user"]["firstName"] == "John"
        assert data["data"]["user"]["lastName"] == "Doe"

    # It Should Log the user in successfully.
    def test_login_user_successfully(self):
        User.objects.create_user(
            email="login@example.com",
            firstName="Login",
            lastName="User",
            password="password123",
        )
        response = self.client.post(
            "/auth/login",
            data={"email": "login@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Login successful"
        assert "accessToken" in data["data"]
        assert "refreshToken" in data["data"]

    # It Should Fail If Required Fields Are Missing and return a 422 error.
    def test_register_missing_fields(self):
        response = self.client.post(
            "/auth/register", data={"email": "missing@example.com"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "Bad Request"
        assert "errors" in data

    # It Should Fail if there’s Duplicate Email or UserID and return a 422 error.
    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="duplicate@example.com",
            firstName="Duplicate",
            lastName="User",
            password="password123",
        )
        response = self.client.post(
            "/auth/register",
            data={
                "email": "duplicate@example.com",
                "firstName": "New",
                "lastName": "User",
                "password": "newpassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "Bad Request"
        assert "errors" in data
