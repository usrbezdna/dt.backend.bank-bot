import pytest

from django.urls import reverse
from src.app.models import User


@pytest.fixture
def web_api_url():
    def inner_with_tlg_id(tlg_id):
        return reverse('web_api', args=[tlg_id])
    return inner_with_tlg_id


@pytest.fixture
def user_model_without_verified_pn():
    def inner(tlg_id):
        return User(
            tlg_id=tlg_id,
            username="testuser",
            first_name="Still",
            last_name = "Test",
            phone_number = ''
        )
    return inner


@pytest.fixture
def user_model_with_verified_pn():
    def inner(tlg_id):
        return User(
            tlg_id=tlg_id,
            username="testuser",
            first_name="Still",
            last_name = "Test",
            phone_number="+542151252",
        )
    return inner


