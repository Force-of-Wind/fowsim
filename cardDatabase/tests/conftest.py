"""
Shared pytest fixtures for cardDatabase tests.
"""

import pytest
from django.test import Client


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Django test client with logged-in user."""
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, django_user_model):
    """Django test client with admin user."""
    user = django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )
    client.force_login(user)
    return client
