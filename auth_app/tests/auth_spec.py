# tests/auth.spec.py

import pytest
from rest_framework.test import APIClient
from auth_app.models import User


@pytest.mark.django_db
class TestAuthEndpoints:
    client = APIClient()

    def test_register_user_successfully(self):
        response = self.client.post(
            "/auth/register/",
            data={
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
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
        assert data["data"]["user"]["first_name"] == "John"
        assert data["data"]["user"]["last_name"] == "Doe"

    def test_login_user_successfully(self):
        User.objects.create_user(
            email="login@example.com",
            first_name="Login",
            last_name="User",
            password="password123",
        )
        response = self.client.post(
            "/auth/login/",
            data={"email": "login@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Login successful"
        assert "accessToken" in data["data"]
        assert "refreshToken" in data["data"]

    def test_register_missing_fields(self):
        response = self.client.post(
            "/auth/register/", data={"email": "missing@example.com"}
        )
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "Bad Request"
        assert "errors" in data

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="duplicate@example.com",
            first_name="Duplicate",
            last_name="User",
            password="password123",
        )
        response = self.client.post(
            "/auth/register/",
            data={
                "email": "duplicate@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "newpassword123",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "Bad Request"
        assert "errors" in data
